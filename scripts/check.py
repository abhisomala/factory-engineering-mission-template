#!/usr/bin/env python3
"""One command to run every check this template ships.

    python3 scripts/check.py

Runs, in order, and reports one summary line per check:

  1. structural self-validation   scripts/validate.py
  2. validator regressions        scripts/test_validate.py
  3. privacy scan                 scripts/privacy_scan.py
  4. markdown lint                scripts/md_lint.py

This is a runner, not a gate of its own: each check keeps its own rules,
its own exit code, and its own output. The runner's only job is to run
all four even after one fails (so you see every failure in one pass),
print their output, and exit non-zero if ANY of them failed. It never
turns a failure into a pass, and it never reports a check it did not
run: a check that cannot start at all is reported as ERROR, not skipped.

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


def run_check(root: str, script: str) -> tuple[str, int, str]:
    """Run one check. Returns (status, exit_code, output)."""
    path = os.path.join(root, script)
    if not os.path.exists(path):
        return "ERROR", 127, f"{script}: not found at the expected path\n"
    try:
        result = subprocess.run(
            [sys.executable, path],
            cwd=root, capture_output=True, text=True, timeout=900,
        )
    except subprocess.TimeoutExpired:
        return "ERROR", 124, f"{script}: timed out after 900s\n"
    except OSError as exc:
        return "ERROR", 126, f"{script}: could not start ({exc})\n"
    output = (result.stdout or "") + (result.stderr or "")
    return ("PASS" if result.returncode == 0 else "FAIL"), result.returncode, output


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("check.py - run every check this template ships")
    print("repo root: (absolute path omitted)")
    print()
    results: list[tuple[str, str, int]] = []
    for label, script in CHECKS:
        status, code, output = run_check(root, script)
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
