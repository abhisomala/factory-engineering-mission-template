#!/usr/bin/env python3
"""Secret-shape and private-identifier scan for repository content.

Answers one narrow question: does any file that could be committed
contain secret-shaped material (service tokens, private-key blocks,
credential assignments) or private identifiers (email addresses,
absolute home-directory paths)? It is a pattern gate in front of
review, not a proof of privacy. It never sends anything anywhere, and
it never prints a full match: a finding names the rule, the file and
line, and a short redacted prefix only.

Scope: every file `validate.walk_files` walks — everything except
artifact directories (`.git`, `__pycache__`, `.venv`, `node_modules`,
and the like). Runtime record directories (`docs/agent_handoff/`,
`human_tests/`, `agent_reports/`) are included on purpose: their
content is exactly what gets committed and published.

Known limits (stated so a clean run is not over-trusted):
- Pattern matching, not entropy analysis or a real secret detector.
  Novel formats, split tokens, or unnamed blobs can pass. The
  planted-token self-tests in `scripts/test_validate.py` pin only the
  rule set below.
- Placeholder forms are deliberately tolerated (`<...>`, `[...]`,
  `example.` domains, `noreply`, printf-style `%s`) so documentation
  can discuss credentials without tripping the gate; a determined
  author could hide real material in placeholder look-alikes. Review
  and the no-secrets rule still apply.
- Line-oriented: a token wrapped across lines is not caught.

Usage:  python3 scripts/privacy_scan.py   (from the repository root)
Exit code 0 when clean, 1 when findings exist.
"""

from __future__ import annotations

import os
import re
import sys

from validate import walk_files

# (rule name, pattern). Names appear in findings and in the self-tests.
SERVICE_TOKEN_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("service-token (github classic)",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b")),
    ("service-token (github fine-grained)",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("service-token (openai)",
     re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}\b")),
    ("service-token (slack)",
     re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("service-token (aws access key)",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
]
PRIVATE_KEY_RULE: tuple[str, re.Pattern[str]] = (
    "private-key block",
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
)
# A credential-looking name assigned a long opaque value on one line.
ASSIGNMENT_RULE: tuple[str, re.Pattern[str]] = (
    "credential assignment",
    re.compile(
        r"(?im)^.{0,40}\b(api[_-]?key|apikey|secret|token|password|passwd|pwd)"
        r"\b[^:=\n]{0,24}[:=][ \t]*[\"'`]?[A-Za-z0-9+/_=.-]{16,}[\"'`]?\s*$"
    ),
)
EMAIL_RULE: tuple[str, re.Pattern[str]] = (
    "email address",
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b"),
)
HOME_PATH_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("absolute home path",
     re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/")),
    ("absolute home path (windows)",
     re.compile(r"(?i)[a-z]:\\users\\")),
]
# Deliberate placeholder tolerances (see the limits above).
EMAIL_EXEMPT_SUBSTRINGS = ("example.", "noreply")

RULES: list[tuple[str, re.Pattern[str]]] = (
    SERVICE_TOKEN_RULES
    + [PRIVATE_KEY_RULE, ASSIGNMENT_RULE, EMAIL_RULE]
    + HOME_PATH_RULES
)


def redact(match: str) -> str:
    """Never echo a full match; show only a short prefix and length."""
    return f"{match[:6]}… ({len(match)} chars)"


def scan_text(rel: str, text: str) -> list[tuple[int, str, str]]:
    """Return (line, rule name, redacted finding) for every rule hit."""
    findings: list[tuple[int, str, str]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        for name, pattern in RULES:
            for match in pattern.finditer(line):
                if name == EMAIL_RULE[0] and any(
                    exempt in match.group(0).lower()
                    for exempt in EMAIL_EXEMPT_SUBSTRINGS
                ):
                    continue
                findings.append((index, name, redact(match.group(0))))
    return findings


def scan_repository(root: str) -> tuple[list[str], int, int]:
    """Scan every walkable file; return findings plus scan counts."""
    findings: list[str] = []
    scanned = 0
    skipped_binary = 0
    for rel in walk_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as handle:
                text = handle.read()
        except UnicodeError:
            skipped_binary += 1
            continue
        except OSError as error:
            findings.append(f"{rel}: unreadable ({error.__class__.__name__})")
            continue
        scanned += 1
        for line, name, finding in scan_text(rel, text):
            findings.append(f"{name} {rel}:{line} {finding}")
    return findings, scanned, skipped_binary


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("privacy_scan.py - secret-shape and private-identifier scan")
    print(f"repo root: {root}")
    print()
    findings, scanned, skipped_binary = scan_repository(root)
    print(f"files scanned: {scanned} (text); skipped as binary: {skipped_binary}")
    for finding in findings:
        print(f"  FAIL: {finding}")
    print()
    if findings:
        print(f"RESULT: FINDINGS ({len(findings)})")
        print("redacted prefixes only; the full matches are never printed")
        return 1
    print("RESULT: CLEAN (0 findings)")
    print("a clean run means the rule set below found nothing; it is not a"
          " proof of privacy (see the limits in this script's docstring)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
