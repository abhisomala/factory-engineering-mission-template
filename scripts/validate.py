#!/usr/bin/env python3
"""Structural self-validation for the Factory Engineering Mission Template.

This is a deliberately small, dependency-free check of the template's own
structural integrity. It answers one question: *is this copy of the
template complete and internally consistent?* It does not run tests, call
the network, or need git; it only reads files from disk.

It performs two checks:

1. README contents tree.
   The fenced file list under the ``## Repository contents`` heading in
   ``README.md`` must exactly match the files present in the working tree.
   The ``README.md`` file itself is excluded from both sides, because it
   is the document doing the listing. Files under VCS metadata
   (``.git/``) and common ignored artifacts (``__pycache__/``, ``.venv/``,
   ``node_modules/``, ``*.log``, ``*.pyc``, ``.DS_Store``) are excluded
   from the working-tree side so a routine local run does not trip the
   check. Documented runtime paths (``docs/agent_handoff/``,
   ``human_tests/``, ``agent_reports/``) are excluded from both sides:
   adopters create them after copying the template, so they are not part
   of the shipped layout the tree describes.

2. Internal file references.
   Every *inline code span* (single backtick, as used throughout the
   template's prose) that names a repo-relative file with a known
   extension (``.md``, ``.py``, and a few config formats) must resolve to
   a file that exists on disk. Markdown links are not used in this
   template; the reference surface is inline code spans in prose. Fenced
   code blocks (```` ``` ````/```` ~~~ ````) are excluded, because they hold
   commands, pasted outputs, and illustrative examples rather than
   normative references. Section markers (`` §5``) and anchors
   (``#bootstrap``) are stripped before the check.

   Documented *runtime* paths -- ``docs/agent_handoff/``, ``human_tests/``,
   and ``agent_reports/`` -- are created by adopters of the template, not
   shipped in it, so they are counted as documented runtime paths and are
   never treated as broken references. Bare filenames that are not
   top-level files (for example ``PENDING.md`` or ``YYYY-MM-DD.md``) and
   tokens containing placeholders (``<file>``, ``<id>``) are likewise
   reported as skipped, not failed.

Exit code is 0 when every check passes, 1 otherwise. Output is concise and
names every offending reference (file, line, and token) on failure.

Usage:  python3 scripts/validate.py
"""

from __future__ import annotations

import os
import re
import sys

# Directories and files that are not part of the shipped template layout and
# must not affect the contents-tree comparison.
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES = (".pyc", ".log")

# Extensions that make a backtick token a checkable file reference.
CHECKED_EXTENSIONS = (
    ".md",
    ".py",
    ".sh",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".cfg",
    ".ini",
    ".txt",
)

# Runtime paths created by adopters, documented by the template but not
# shipped in it. References into these are reported, never failed.
RUNTIME_PREFIXES = (
    "docs/agent_handoff/",
    "human_tests/",
    "agent_reports/",
)

# A single-backtick inline code span, excluding runs of two or more
# backticks (which delimit fenced code blocks) and never spanning newlines.
INLINE_SPAN_RE = re.compile(r"(?<!`)`(?!`)([^`\n]+)`(?!`)")

# A repo-relative path token: starts alphanumeric/dot, then path characters.
PATH_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*$")

CONTENTS_HEADING_RE = re.compile(r"^##\s+Repository contents\s*$")


def is_runtime_path(rel: str) -> bool:
    """True for documented runtime paths that adopters create, not the template."""
    return any(rel.startswith(prefix) for prefix in RUNTIME_PREFIXES)


def repo_root() -> str:
    """Return the repository root: the parent of this script's directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def walk_files(root: str) -> list[str]:
    """All files under root, as repo-relative POSIX paths, ignoring artifacts."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for name in filenames:
            if name in IGNORED_FILES or name.endswith(IGNORED_SUFFIXES):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            found.append(rel)
    return sorted(found)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def parse_contents_tree(readme_text: str) -> list[str] | None:
    """First whitespace token of each line in the README contents fence."""
    lines = readme_text.splitlines()
    heading = next(
        (i for i, ln in enumerate(lines) if CONTENTS_HEADING_RE.match(ln)), None
    )
    if heading is None:
        return None
    cursor = heading + 1
    while cursor < len(lines) and not lines[cursor].startswith("```"):
        cursor += 1
    if cursor >= len(lines):
        return None
    entries: list[str] = []
    cursor += 1
    while cursor < len(lines) and not lines[cursor].startswith("```"):
        stripped = lines[cursor].strip()
        if stripped:
            entries.append(stripped.split()[0])
        cursor += 1
    return entries


def normalize_token(token: str) -> str | None:
    """Turn a raw backtick token into a checkable path, or None to skip it."""
    token = token.strip("`'\"(),.;:[]{}")
    if not token:
        return None
    if any(ch in token for ch in "<>*?$"):
        return None
    if "#" in token:
        token = token.split("#", 1)[0]
    if token.startswith("./"):
        token = token[2:]
    if not token or token.startswith("/"):
        return None
    if not token.endswith(CHECKED_EXTENSIONS):
        return None
    if not PATH_TOKEN_RE.match(token):
        return None
    return token


def iter_prose_lines(text: str):
    """Yield (line_number, line) for lines outside fenced code blocks."""
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield line_no, line


def check_references(root: str, files: list[str]) -> dict:
    """Check inline-code file references in the prose of every markdown file."""
    top_level = set(os.listdir(root))
    result = {
        "files_scanned": 0,
        "spans_seen": 0,
        "checked": 0,
        "runtime": 0,
        "skipped": 0,
        "failures": [],  # (rel_path, line_no, token)
    }
    for rel in files:
        if not rel.endswith(".md"):
            continue
        result["files_scanned"] += 1
        text = read_text(os.path.join(root, rel))
        for line_no, line in iter_prose_lines(text):
            for match in INLINE_SPAN_RE.finditer(line):
                result["spans_seen"] += 1
                for raw in match.group(1).split():
                    token = normalize_token(raw)
                    if token is None:
                        continue
                    if is_runtime_path(token):
                        result["runtime"] += 1
                        continue
                    if "/" in token:
                        if token.split("/", 1)[0] not in top_level:
                            result["skipped"] += 1
                            continue
                    elif token not in top_level:
                        result["skipped"] += 1
                        continue
                    if not os.path.exists(os.path.join(root, token)):
                        result["failures"].append((rel, line_no, token))
                    else:
                        result["checked"] += 1
    return result


def main() -> int:
    root = repo_root()
    print("validate.py - structural self-validation")
    print(f"repo root: {root}")
    print()

    files = walk_files(root)
    readme_path = os.path.join(root, "README.md")
    readme_text = read_text(readme_path)

    # Check 1: README contents tree vs the working tree.
    print("[1/2] README 'Repository contents' tree vs working tree")
    tree = parse_contents_tree(readme_text)
    tree_failures: list[str] = []
    if tree is None:
        tree_failures.append(
            "could not find the fenced file list under '## Repository contents'"
        )
        print("  FAIL: no '## Repository contents' fenced block found")
    else:
        disk = {f for f in files if f != "README.md" and not is_runtime_path(f)}
        listed = {t for t in tree if not is_runtime_path(t)}
        on_disk_not_listed = sorted(disk - listed)
        listed_not_on_disk = sorted(listed - disk)
        print(f"  tree entries (runtime paths excluded): {len(listed)}")
        print(f"  files on disk (README.md + runtime paths excluded): {len(disk)}")
        if on_disk_not_listed:
            tree_failures.append(
                "on disk but missing from the tree: " + ", ".join(on_disk_not_listed)
            )
        if listed_not_on_disk:
            tree_failures.append(
                "listed in the tree but not on disk: " + ", ".join(listed_not_on_disk)
            )
        if tree_failures:
            for problem in tree_failures:
                print(f"  FAIL: {problem}")
        else:
            print("  PASS: tree matches disk exactly")
    print()

    # Check 2: internal file references in markdown.
    print("[2/2] Internal file references in *.md (inline code spans)")
    refs = check_references(root, files)
    print(f"  markdown files scanned: {refs['files_scanned']}")
    print(f"  inline code spans seen: {refs['spans_seen']}")
    print(f"  repo-relative references checked: {refs['checked']}")
    print(f"  documented runtime paths (not shipped, not failed): {refs['runtime']}")
    print(f"  non-path / bare / placeholder tokens skipped: {refs['skipped']}")
    if refs["failures"]:
        for rel, line_no, token in refs["failures"]:
            print(f"  FAIL: {rel}:{line_no}: unresolved reference `{token}`")
    else:
        print("  PASS: every checked reference resolves on disk")
    print()

    failed = bool(tree_failures) or bool(refs["failures"])
    checks_passed = 2 - (1 if tree_failures else 0) - (1 if refs["failures"] else 0)
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({checks_passed}/2 checks passed)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
