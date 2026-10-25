#!/usr/bin/env python3
"""One command to run every check this template ships.

    python3 scripts/check.py

Runs, in order, and reports one summary line per check:

  1. structural self-validation   scripts/validate.py
  2. validator regressions        scripts/test_validate.py
  3. privacy scan                 scripts/privacy_scan.py
  4. markdown lint                scripts/md_lint.py

This is a runner, not a gate of its own: each check keeps its own rules,
its own exit code, and its own output. The runner's job is to run all
four even after one fails (so you see every failure in one pass), print
their output, and exit non-zero if ANY of them failed.

Three statuses, and the distinction matters:

  PASS   the check ran and exited 0.
  FAIL   the check ran and exited non-zero — its own verdict.
  ERROR  the check could not run at all: missing, not a regular file,
         not readable, unstartable, timed out, or its output could not be
         read. An unrunnable check is never reported as PASS and never as
         FAIL, because the check never reached a verdict.

Output handling: a sub-check's output is forwarded with this repository's
absolute root replaced by "<repo root>", so a run never prints the
operator's home directory layout. Undecodable bytes are replaced, not
raised: a check that writes invalid UTF-8 still gets its real exit code
and the remaining checks still run.

Exit code: 0 only when all four checks passed.

Usage:  python3 scripts/check.py   (from the repository root)
"""

from __future__ import annotations

import os
import subprocess
import sys

CHECKS = (
    ("structural self-validation", "scripts/validate.py"),
    ("validator regressions", "scripts/test_validate.py"),
    ("privacy scan", "scripts/privacy_scan.py"),
    ("markdown lint", "scripts/md_lint.py"),
)

TIMEOUT_SECONDS = 900


def make_sanitizer(root: str):
    """Return a function replacing this repository's absolute root.

    Both the given root and its OS-resolved path (a different string when
    the checkout sits behind a symlink) are replaced, so neither spelling
    reaches the output.

    Stated limit: those are the two spellings a check can print without
    contriving a third. A check that builds a path to this same directory
    where an intermediate component stays unresolved while this root
    resolved it is not covered. The runner takes its root from its own
    __file__ and the checks compute theirs the same way, so the two
    candidates above are the realistic set — this paragraph exists so the
    guarantee is not overstated.
    """
    candidates = [root, os.path.realpath(root)]
    ordered = sorted(set(candidates), key=len, reverse=True)

    def sanitize(text: str) -> str:
        for candidate in ordered:
            text = text.replace(candidate, "<repo root>")
        return text

    return sanitize


def run_check(root: str, script: str, sanitize) -> tuple[str, int, str]:
    """Run one check. Returns (status, exit_code, output).

    Status is PASS / FAIL / ERROR as documented in the module docstring.
    """
    path = os.path.join(root, script)
    # Preflight: a check that cannot even be read never ran, so its
    # absence of a verdict is ERROR, not FAIL.
    if not os.path.exists(path):
        return "ERROR", 127, f"{script}: not found at the expected path\n"
    if not os.path.isfile(path):
        return "ERROR", 126, f"{script}: not a regular file\n"
    if not os.access(path, os.R_OK):
        return "ERROR", 126, f"{script}: not readable\n"
    try:
        result = subprocess.run(
            [sys.executable, path],
            cwd=root,
            capture_output=True,
            # errors="replace": invalid bytes must not abort the whole run
            # and must not hide the check's real exit code.
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return "ERROR", 124, f"{script}: timed out after {TIMEOUT_SECONDS}s\n"
    except OSError as exc:
        # Do not interpolate exc: its text can carry an absolute path.
        return "ERROR", 126, f"{script}: could not start ({type(exc).__name__})\n"
    output = sanitize((result.stdout or "") + (result.stderr or ""))
    return ("PASS" if result.returncode == 0 else "FAIL"), result.returncode, output


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sanitize = make_sanitizer(root)
    print("check.py - run every check this template ships")
    print("repo root: (absolute path omitted)")
    print()
    results: list[tuple[str, str, int]] = []
    for label, script in CHECKS:
        status, code, output = run_check(root, script, sanitize)
        results.append((label, status, code))
        print(f"===== {label} ({script}) =====")
        for line in output.splitlines():
            print(f"  {line}")
        print(f"----- {status}: {label} (exit {code})")
        print()
    failed = [label for label, status, _ in results if status != "PASS"]
    print("summary:")
    for label, status, code in results:
        print(f"  {status:5} {label}")
    print()
    if failed:
        print(f"RESULT: FAIL ({len(failed)}/{len(CHECKS)} checks did not pass:"
              f" {', '.join(failed)})")
        return 1
    print(f"RESULT: PASS ({len(CHECKS)}/{len(CHECKS)} checks passed)")
    print("all four checks are green; this is a clean local run, not host"
          " evidence and not a proof of privacy (see each script's limits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
