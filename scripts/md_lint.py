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

1. Fenced code blocks are balanced: every ``` or ~~~ opener has a
   closer before end of file. An unclosed fence silently changes which
   lines every other tool treats as prose. (Whole file.)
2. No heading level jumps: a heading may go deeper by at most one
   level at a time (an H1 followed directly by an H3 is an error).
   Coming back up (H4 -> H2) is always allowed.
3. Exactly one H1 per file — except under `agent_reports/`, where
   dated records may stack several day sections in one file, each with
   its own H1. That exemption is the documented reason, not a
   convenience: those records are append-only history.
4. No trailing whitespace on prose lines. (Whitespace inside fenced
   blocks is content and is not touched.)
5. The file ends with exactly one newline: neither missing nor
   followed by blank lines.

Known limits: this is not a general Markdown parser — setext headings
(underlined with === or ---) are not treated as headings (this
repository uses ATX headings only), HTML blocks are not fenced
content, and reference-style link definitions are not checked. A CLEAN
run means these five structural rules held; it says nothing about
prose quality or link targets (which `scripts/validate.py` checks
separately for inline references).

Usage:  python3 scripts/md_lint.py   (from the repository root)
Exit code 0 when clean, 1 when findings exist.
"""

from __future__ import annotations

import os
import re
import sys

from validate import walk_files

HEADING_RE = re.compile(r"^(#{1,6})(\s+\S.*)?$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
H1_EXEMPT_PREFIX = "agent_reports/"


def lint_text(rel: str, text: str) -> list[str]:
    """Return one diagnostic per structural rule violation."""
    findings: list[str] = []

    in_fence = False
    fence_line = 0
    level = 0
    h1_count = 0
    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        if FENCE_RE.match(line):
            if not in_fence:
                in_fence = True
                fence_line = index
            else:
                in_fence = False
            continue
        if in_fence:
            continue
        if line.rstrip() != line:
            findings.append(
                f"{rel}:{index}: trailing whitespace on a prose line"
            )
        stripped = line.lstrip()
        heading = HEADING_RE.match(stripped)
        if heading and not line.startswith(" " * 4):
            depth = len(heading.group(1))
            if depth == 1:
                h1_count += 1
            if depth > level + 1:
                findings.append(
                    f"{rel}:{index}: heading level jump: H{level} -> H{depth}"
                    if level
                    else f"{rel}:{index}: file starts below H1 (H{depth})"
                )
            level = depth
    if in_fence:
        findings.append(
            f"{rel}:{fence_line}: unclosed fenced code block"
        )
    if not rel.startswith(H1_EXEMPT_PREFIX):
        if h1_count == 0:
            findings.append(f"{rel}: no H1 heading")
        elif h1_count > 1:
            findings.append(f"{rel}: {h1_count} H1 headings (expected 1)")
    if not text:
        findings.append(f"{rel}: empty file")
    elif not text.endswith("\n"):
        findings.append(f"{rel}: missing final newline")
    elif text.endswith("\n\n"):
        findings.append(f"{rel}: trailing blank line(s) at end of file")
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
        return 1
    print("RESULT: CLEAN (0 findings)")
    print("a clean run means the five structural rules held; it is not a"
          " prose-quality or link-target judgment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
