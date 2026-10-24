#!/usr/bin/env python3
"""Structural markdown lint for every markdown file in the repository.

Small, stdlib-only, and deliberately structural: it checks the shapes
that, when broken, corrupt how the other tools read the file — heading
hierarchy, fence balance, trailing whitespace, final newline — not
prose style or line length. Line length is intentionally not linted:
this repository's formats include one-line-per-file tables and wrapped
prose where any fixed width would be arbitrary.

Rules (applied to prose, i.e. lines outside fenced code blocks, except
where noted):

1. Fenced code blocks are balanced: an opener (``` or ~~~ of three or
   more, optionally with an info string; up to three leading spaces) is
   closed only by a fence of the SAME character, at least the SAME
   length, followed by nothing but spaces. A fence of the other
   character, a shorter run, or a run with trailing text does not close
   it — so a four-backtick block can contain three-backtick examples.
   An unclosed fence silently changes which lines every other tool
   treats as prose. (Whole file.)
2. No heading level jumps: a heading may go deeper by at most one
   level at a time (an H1 followed directly by an H3 is an error).
   Coming back up (H4 -> H2) is always allowed.
3. At least one H1 per file; exactly one everywhere except under
   `agent_reports/`, where dated records may stack several day sections
   in one file, each with its own H1 — so MULTIPLE H1s are allowed
   there, but at least one is still required. The exemption is the
   documented reason, not a convenience: those records are append-only
   history.
4. No trailing whitespace on prose lines. (Whitespace inside fenced
   blocks is content and is not touched.)
5. The file ends with exactly one newline: neither missing nor
   followed by blank lines.

Diagnostics are printed with sanitized paths (`privacy_scan` rules):
a secret-shaped filename must never be echoed by a lint finding.

Known limits: this is not a general Markdown parser — setext headings
(underlined with === or ---) are not treated as headings (this
repository uses ATX headings only), HTML blocks are not fenced content,
and reference-style link definitions are not checked. A CLEAN run
means these five structural rules held; it says nothing about prose
quality or link targets (which `scripts/validate.py` checks separately
for inline references).

Usage:  python3 scripts/md_lint.py   (from the repository root)
Exit code 0 when clean, 1 when findings exist.
"""

from __future__ import annotations

import os
import re
import sys

from privacy_scan import sanitize_display
from validate import walk_files

FENCE_RUN_RE = re.compile(r"^(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})(\s+\S.*)?$")
H1_EXEMPT_PREFIX = "agent_reports/"


def fence_delimiter(line: str) -> tuple[str, int, str] | None:
    """A fence delimiter candidate: (character, length, trailing text).

    Up to three leading spaces are allowed. Returns None for any other
    line. Whether a candidate actually opens or closes a fence depends
    on the state in lint_text (same character, at least the same
    length, and a closer must be followed by nothing but spaces).
    """
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > 3:
        return None
    match = FENCE_RUN_RE.match(stripped)
    if not match:
        return None
    return match.group(1)[0], len(match.group(1)), stripped[match.end():]


def lint_text(rel: str, text: str) -> list[str]:
    """Return one diagnostic per structural rule violation."""
    findings: list[str] = []
    srel = sanitize_display(rel)
    in_fence = ""
    fence_len = 0
    fence_line = 0
    level = 0
    h1_count = 0
    for index, line in enumerate(text.splitlines(), start=1):
        fence = fence_delimiter(line)
        if in_fence:
            if (fence and fence[0] == in_fence and fence[1] >= fence_len
                    and not fence[2].strip()):
                in_fence = ""
            continue
        if fence:
            if fence[0] == "`" and "`" in fence[2]:
                pass  # not a valid opener (backtick in info string): prose
            else:
                in_fence, fence_len, fence_line = fence[0], fence[1], index
                continue
        if line.rstrip() != line:
            findings.append(
                f"{srel}:{index}: trailing whitespace on a prose line"
            )
        stripped = line.lstrip()
        heading = HEADING_RE.match(stripped)
        if heading and not line.startswith("    "):
            depth = len(heading.group(1))
            if depth == 1:
                h1_count += 1
            if depth > level + 1:
                findings.append(
                    f"{srel}:{index}: heading level jump: H{level} -> H{depth}"
                    if level
                    else f"{srel}:{index}: file starts below H1 (H{depth})"
                )
            level = depth
    if in_fence:
        findings.append(f"{srel}:{fence_line}: unclosed fenced code block")
    if h1_count == 0:
        findings.append(f"{srel}: no H1 heading")
    elif h1_count > 1 and not rel.startswith(H1_EXEMPT_PREFIX):
        findings.append(f"{srel}: {h1_count} H1 headings (expected 1)")
    if not text:
        findings.append(f"{srel}: empty file")
    elif not text.endswith("\n"):
        findings.append(f"{srel}: missing final newline")
    elif text.endswith("\n\n"):
        findings.append(f"{srel}: trailing blank line(s) at end of file")
    return findings


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("md_lint.py - structural markdown lint")
    print("repo root: (absolute path omitted)")
    print()
    findings: list[str] = []
    scanned = 0
    for rel in walk_files(root):
        if not rel.endswith(".md"):
            continue
        with open(os.path.join(root, rel), encoding="utf-8") as handle:
            findings.extend(lint_text(rel, handle.read()))
        scanned += 1
    print(f"markdown files scanned: {scanned}")
    for finding in findings:
        print(f"  FAIL: {finding}")
    print()
    if findings:
        print(f"RESULT: FINDINGS ({len(findings)})")
        print("diagnostic paths are sanitized (privacy-scan rules);"
              " secret-shaped filenames are never echoed")
        return 1
    print("RESULT: CLEAN (0 findings)")
    print("a clean run means the five structural rules held; it is not a"
          " prose-quality or link-target judgment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
