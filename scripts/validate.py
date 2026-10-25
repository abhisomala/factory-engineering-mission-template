#!/usr/bin/env python3
"""Structural self-validation for the Factory Engineering Mission Template.

This is a deliberately small, dependency-free check of the template's own
structural integrity. It answers one question: *is this copy of the
template complete and internally consistent?* It does not run tests, call
the network, or need git; it only reads files from disk.

It performs three checks:

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

3. Worked-example schemas.
   The three shipped examples must retain their section-scoped fenced
   artifacts and required fields. These are structure-only checks of
   synthetic material, not proof of outcomes, authorization, or live hosts.
   The exact checks and limitations are in docs/worked-example-schema.md.

Exit code is 0 when every check passes, 1 otherwise. Output is concise and
names every offending reference (file, line, and token) on failure.

Adopted-repository mode (``--adopted``) answers a different question:
*has a repository that adopted this template completed the quickstart's
bootstrap outputs, and are they internally consistent?* It checks the
three runtime directories, the four day-one bundle files,
``human_tests/PENDING.md``, the host-validation-queue shape, the
manifest hashes (tolerating the ``shasum``/``sha256sum`` difference), and
whether the ``AGENTS.md`` risk-surface placeholder has been replaced. It
proves existence and internal consistency only — the external gates
(ruleset, credential scope, tracker labels, a live Mission) are paired
with these machine checks in ``templates/readiness-checklist.md`` for a
human to verify. The plain mode above is unchanged by this flag.

Usage:  python3 scripts/validate.py              (template self-check)
        python3 scripts/validate.py --adopted   (adopted-repo readiness)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

from worked_examples import check_worked_examples

# Directories and files that are not part of the shipped template layout and
# must not affect the contents-tree comparison. In a git worktree, `.git` is
# a file rather than a directory, so IGNORED_DIRS alone does not exclude it.
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
IGNORED_FILES = {".git", ".DS_Store", "Thumbs.db"}
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


# --- Adopted-repository readiness mode (--adopted) -----------------------
#
# The checks below answer a different question from the template checks: *has a
# repository that adopted this template completed the quickstart's
# bootstrap outputs, and are they internally consistent?* They prove
# existence and internal consistency only. The external gates — ruleset
# on, credential scope, tracker labels, a live Mission — are listed for a
# human in templates/readiness-checklist.md.

ADOPTED_RUNTIME_DIRS = ("docs/agent_handoff", "human_tests", "agent_reports")
ADOPTED_BUNDLE_FILES = (
    "docs/agent_handoff/00_README.md",
    "docs/agent_handoff/HOST_VALIDATION_QUEUE.md",
    "docs/agent_handoff/MANIFEST.md",
)
ADOPTED_BUNDLE_DIR = "docs/agent_handoff/10_durable_instructions"
ADOPTED_PENDING = "human_tests/PENDING.md"
ADOPTED_HVQ = "docs/agent_handoff/HOST_VALIDATION_QUEUE.md"
ADOPTED_MANIFEST = "docs/agent_handoff/MANIFEST.md"
AGENTS_MD = "AGENTS.md"
RISK_SURFACES_HEADING = "### This project's risk surfaces"
RISK_PLACEHOLDER_MARKER = "YOUR PROJECT'S R2/R3 SURFACES"
RISK_EDIT_ME_MARKER = "[EDIT ME"
HVQ_DATED_PREFIX = "## Dated status block"
HVQ_TABLE_PREFIX = "| ID |"
HVQ_DATE_PLACEHOLDER = "[DATE]"
# sha256sum (Linux) writes "<64-hex>  <path>"; shasum -a 256 (stock macOS)
# writes "<64-hex>  <path>" (text) or "<64-hex> *<path>" (binary). One
# regex tolerates all three shapes.
MANIFEST_ENTRY_RE = re.compile(r"^([0-9a-f]{64})[ \t]+\*?[ \t]*(\S.*?)\s*$")
MANIFEST_REQUIRED = (
    "docs/agent_handoff/00_README.md",
    "docs/agent_handoff/HOST_VALIDATION_QUEUE.md",
)


def sha256_of(path: str) -> str | None:
    """Hex sha256 of a file's bytes, or None if it cannot be read."""
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def nonempty_md_files(root: str, rel_dir: str) -> list[str]:
    """Names of non-empty *.md files directly inside rel_dir."""
    full = os.path.join(root, rel_dir)
    if not os.path.isdir(full):
        return []
    found: list[str] = []
    for name in sorted(os.listdir(full)):
        candidate = os.path.join(full, name)
        if not os.path.isfile(candidate) or not name.endswith(".md"):
            continue
        try:
            if os.path.getsize(candidate) > 0:
                found.append(name)
        except OSError:
            pass
    return found


def parse_manifest(root: str) -> tuple[dict[str, str], list[str]]:
    """Parse MANIFEST.md hash lines outside fenced code blocks.

    Returns (entries: rel path -> expected sha256 hex, problems: messages
    for lines that are malformed by convention, e.g. a self-entry).
    """
    entries: dict[str, str] = {}
    problems: list[str] = []
    path = os.path.join(root, ADOPTED_MANIFEST)
    if not os.path.isfile(path):
        return entries, problems
    for _line_no, line in iter_prose_lines(read_text(path)):
        match = MANIFEST_ENTRY_RE.match(line.strip())
        if match is None:
            continue
        digest, rel = match.group(1), match.group(2).strip()
        rel = rel.lstrip("./").replace(os.sep, "/")
        if rel == ADOPTED_MANIFEST:
            problems.append(
                "MANIFEST.md lists itself — a file cannot contain its own "
                "checksum; remove that entry"
            )
            continue
        entries[rel] = digest
    return entries, problems


def adopted_checks(root: str) -> list[tuple[str, bool, list[str]]]:
    """The six adopted-repo readiness checks: (title, passed, output)."""

    results: list[tuple[str, bool, list[str]]] = []

    # 1. Runtime directories.
    lines: list[str] = []
    passed = True
    for rel_dir in ADOPTED_RUNTIME_DIRS:
        if os.path.isdir(os.path.join(root, rel_dir)):
            lines.append(f"  {rel_dir}/ present")
        else:
            passed = False
            lines.append(f"  FAIL: runtime directory missing: {rel_dir}/")
    if passed:
        lines.append("  PASS: all runtime directories exist")
    results.append(("Runtime directories", passed, lines))

    # 2. Day-one bundle files, non-empty.
    lines = []
    passed = True
    for rel_file in ADOPTED_BUNDLE_FILES:
        full = os.path.join(root, rel_file)
        if not os.path.isfile(full):
            passed = False
            lines.append(f"  FAIL: bundle file missing: {rel_file}")
        elif os.path.getsize(full) == 0:
            passed = False
            lines.append(f"  FAIL: bundle file exists but is empty: {rel_file}")
        else:
            lines.append(f"  {rel_file} non-empty")
    durable = nonempty_md_files(root, ADOPTED_BUNDLE_DIR)
    if durable:
        lines.append(
            f"  {ADOPTED_BUNDLE_DIR}/ has {len(durable)} non-empty file(s)"
        )
    else:
        passed = False
        lines.append(
            f"  FAIL: {ADOPTED_BUNDLE_DIR}/ missing or empty (needs the "
            "dated decision record + rules/red-lines starter)"
        )
    if passed:
        lines.append("  PASS: all four day-one bundle outputs exist non-empty")
    results.append(("Day-one bundle files", passed, lines))

    # 3. human_tests/PENDING.md.
    lines = []
    if os.path.isfile(os.path.join(root, ADOPTED_PENDING)):
        lines.append("  PASS: human_tests/PENDING.md exists")
        results.append(("human_tests/PENDING.md", True, lines))
    else:
        lines.append("  FAIL: human_tests/PENDING.md missing")
        results.append(("human_tests/PENDING.md", False, lines))

    # 4. Host validation queue shape.
    lines = []
    passed = True
    hvq_path = os.path.join(root, ADOPTED_HVQ)
    if not os.path.isfile(hvq_path):
        passed = False
        lines.append(f"  FAIL: queue file missing: {ADOPTED_HVQ}")
    else:
        hvq_lines = read_text(hvq_path).splitlines()
        dated = [ln for ln in hvq_lines if ln.startswith(HVQ_DATED_PREFIX)]
        if not dated:
            passed = False
            lines.append(f"  FAIL: no '{HVQ_DATED_PREFIX}' header found")
        elif any(HVQ_DATE_PLACEHOLDER in ln for ln in dated):
            passed = False
            lines.append(
                "  FAIL: the dated status block still carries the [DATE] "
                "placeholder — replace it with the actual date"
            )
        if not any(ln.startswith(HVQ_TABLE_PREFIX) for ln in hvq_lines):
            passed = False
            lines.append(
                f"  FAIL: no table header row starting '{HVQ_TABLE_PREFIX} ...'"
            )
        if passed:
            lines.append(
                "  PASS: dated status block (filled) + table header present"
            )
    results.append(("Host validation queue shape", passed, lines))

    # 5. MANIFEST integrity hashes.
    lines = []
    passed = True
    entries, problems = parse_manifest(root)
    for problem in problems:
        passed = False
        lines.append(f"  FAIL: {problem}")
    if not entries:
        passed = False
        lines.append(
            "  FAIL: no hash entries (one line per day-one bundle file; "
            "sha256sum on Linux, shasum -a 256 on stock macOS)"
        )
    else:
        for rel in sorted(entries):
            actual = sha256_of(os.path.join(root, rel))
            if actual is None:
                passed = False
                lines.append(f"  FAIL: entry points at a missing file: {rel}")
            elif actual != entries[rel]:
                passed = False
                lines.append(
                    f"  FAIL: hash mismatch: {rel} — manifest says "
                    f"{entries[rel]}, file hashes {actual}; re-hash in the "
                    "same commit as the change"
                )
        for required in MANIFEST_REQUIRED:
            if required not in entries:
                passed = False
                lines.append(
                    f"  FAIL: day-one file not covered by the manifest: "
                    f"{required}"
                )
        if passed:
            noun = "entry" if len(entries) == 1 else "entries"
            lines.append(
                f"  PASS: {len(entries)} {noun}, all match the files on "
                "disk; day-one files covered"
            )
    results.append(("MANIFEST integrity hashes", passed, lines))

    # 6. AGENTS.md risk surfaces.
    lines = []
    passed = True
    agents_path = os.path.join(root, AGENTS_MD)
    if not os.path.isfile(agents_path):
        passed = False
        lines.append("  FAIL: AGENTS.md not found")
    else:
        agents_text = read_text(agents_path)
        if RISK_SURFACES_HEADING not in agents_text:
            passed = False
            lines.append(
                f"  FAIL: the '{RISK_SURFACES_HEADING}' block is missing "
                "(the placeholder was deleted instead of replaced)"
            )
        if RISK_PLACEHOLDER_MARKER in agents_text:
            passed = False
            lines.append(
                "  FAIL: the 'YOUR PROJECT'S R2/R3 SURFACES — edit me' "
                "placeholder is still present — replace it with your "
                "project's R2/R3 definitions"
            )
        if RISK_EDIT_ME_MARKER in agents_text:
            passed = False
            lines.append(
                "  FAIL: the risk-surfaces block still contains '[EDIT ME' "
                "placeholders — fill them in"
            )
        if passed:
            lines.append(
                "  PASS: 'This project's risk surfaces' present and filled in"
            )
    results.append(("AGENTS.md risk surfaces", passed, lines))

    return results


def parse_args() -> argparse.Namespace:
    """Parse the command line; adopted mode remains separate from plain mode."""
    parser = argparse.ArgumentParser(
        description=(
            "Structural self-validation for the template itself, or "
            "(with --adopted) readiness checks for a repository that "
            "adopted the template."
        )
    )
    parser.add_argument(
        "--adopted",
        action="store_true",
        help=(
            "check an adopted repository's bootstrap outputs instead of "
            "the template's shipped structure"
        ),
    )
    return parser.parse_args()


def main_adopted() -> int:
    root = repo_root()
    print("validate.py --adopted - adopted-repository readiness check")
    print("repo root: (absolute path omitted)")
    print()
    results = adopted_checks(root)
    for index, (title, _passed, lines) in enumerate(results, start=1):
        print(f"[{index}/6] {title}")
        for line in lines:
            print(line)
        print()
    checks_passed = sum(1 for _t, passed, _l in results if passed)
    failed = checks_passed < len(results)
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({checks_passed}/6 checks passed)")
    return 1 if failed else 0


def main() -> int:
    if parse_args().adopted:
        return main_adopted()
    root = repo_root()
    print("validate.py - structural self-validation")
    print("repo root: (absolute path omitted)")
    print()

    files = walk_files(root)
    readme_path = os.path.join(root, "README.md")
    readme_text = read_text(readme_path)

    # Check 1: README contents tree vs the working tree.
    print("[1/3] README 'Repository contents' tree vs working tree")
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
    print("[2/3] Internal file references in *.md (inline code spans)")
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

    # Check 3: shape of the shipped synthetic examples, never their truth.
    print("[3/3] Worked-example schemas (structure only; synthetic, not live evidence)")
    example_failures = check_worked_examples(root)
    if example_failures:
        for problem in example_failures:
            print(f"  FAIL: {problem}")
    else:
        print("  PASS: all three examples have the required structured artifacts")
    print()

    failed_checks = sum(bool(problems) for problems in
                        (tree_failures, refs["failures"], example_failures))
    failed = failed_checks > 0
    checks_passed = 3 - failed_checks
    print(f"RESULT: {'FAIL' if failed else 'PASS'} ({checks_passed}/3 checks passed)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
