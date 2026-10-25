#!/usr/bin/env python3
"""Repeatable, offline validator regressions in disposable synthetic copies."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
from unittest import mock
import unittest

import validate
from worked_examples import (
    CONTRACT_FIELDS, EXAMPLE_PATHS, HANDOFF_SECTIONS, QUEUE_COLUMNS,
    REQUEST_FIELDS, REVIEW_FIELDS, Schema, check_worked_examples,
)

ROOT = Path(__file__).resolve().parent.parent


class ValidatorRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Registered files only: never copy an adopter's ignored local data.
        tree = validate.parse_contents_tree((ROOT / "README.md").read_text(encoding="utf-8"))
        if tree is None:
            raise AssertionError("fixture source needs the README contents tree")
        cls.snapshot = {}
        for rel in ["README.md", *tree]:
            path = (ROOT / rel).resolve()
            if ROOT not in path.parents:
                raise AssertionError("fixture source must stay inside this repository")
            cls.snapshot[rel] = path.read_bytes()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mission-validator-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel, content in self.snapshot.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def text(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def cli(self, *args):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/validate.py"), *args],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )
        # Sanitize captured paths in assertion details, not just successful runs.
        output = result.stdout.replace(str(self.root), "<fixture>")
        self.assertEqual(result.stderr.replace(str(self.root), "<fixture>"), "")
        return result.returncode, output

    def negative(self, path, changed, diagnostic):
        original = self.text(path)
        self.assertNotEqual(original, changed, "mutation must change the fixture")
        try:
            self.write(path, changed)
            failures = check_worked_examples(str(self.root))
            self.assertTrue(failures, "isolated mutation must fail the schema")
            self.assertTrue(any(path in f and diagnostic in f for f in failures),
                            "\n".join(failures))
            self.assertTrue(all(f.startswith(path + ":") for f in failures))
        finally:
            self.write(path, original)

    def rename_fields(self, path, labels, occurrences=1, bullet=False):
        original = self.text(path)
        for label in labels:
            prefix = r"^- " if bullet else r"^(?:- )?"
            pattern = re.compile(prefix + re.escape(label) + ":", re.MULTILINE)
            matches = list(pattern.finditer(original))
            self.assertEqual(len(matches), occurrences, label)
            for index, match in enumerate(matches):
                with self.subTest(label=label, artifact=index + 1):
                    changed = original[:match.start()] + "REMOVED:" + original[match.end():]
                    self.negative(path, changed, f"field '{label}'")

    def test_all_three_shipped_examples(self):
        self.assertEqual(check_worked_examples(str(self.root)), [])

    def test_plain_cli_positive(self):
        code, output = self.cli()
        self.assertEqual(code, 0, output)
        for marker in ("[1/3] README", "[2/3] Internal", "[3/3] Worked-example",
                       "structure only; synthetic, not live evidence",
                       "RESULT: PASS (3/3 checks passed)"):
            self.assertIn(marker, output)

    def test_every_contract_field_in_both_lifecycles(self):
        self.rename_fields(EXAMPLE_PATHS[0], CONTRACT_FIELDS, 2)

    def test_empty_and_duplicate_contract_fields(self):
        path = EXAMPLE_PATHS[0]
        original = self.text(path)
        empty = re.sub(r"(?m)^TASK:\n.*?(?=^WHY NOW / BLOCKING WHAT:)",
                       "TASK:\n\n", original, count=1, flags=re.DOTALL)
        self.negative(path, empty, "field 'TASK'")
        self.negative(path, original.replace("TASK:\n", "TASK: duplicate\nTASK:\n", 1),
                      "field 'TASK'")

    def test_handoff_sections_and_branch_fields(self):
        path = EXAMPLE_PATHS[0]
        original = self.text(path)
        for title in HANDOFF_SECTIONS:
            matches = list(re.finditer(r"^## " + re.escape(title) + "$",
                                       original, re.MULTILINE))
            self.assertEqual(len(matches), 2)
            for index, match in enumerate(matches):
                with self.subTest(title=title, artifact=index + 1):
                    self.negative(path, original[:match.start()] + "## Removed" +
                                  original[match.end():], re.escape(title))
        self.rename_fields(path, ("Task/issue", "Branch", "Worktree",
                                 "Base commit (exact SHA)", "Head commit (exact SHA)"), 2)

    def test_every_review_condition(self):
        path = EXAMPLE_PATHS[0]
        original = self.text(path)
        for index, label in enumerate(REVIEW_FIELDS, start=1):
            with self.subTest(condition=index):
                self.negative(path, original.replace(f"{index} {label}:", f"{index} removed:", 1),
                              f"condition {index}")
        self.negative(path, original.replace("VERDICT: APPROVE", "VERDICT: maybe", 1),
                      "invalid verdict")

    def test_tracker_and_merge_artifacts(self):
        path = EXAMPLE_PATHS[0]
        self.rename_fields(path, ("State", "Labels", "Body"), 2)
        original = self.text(path)
        self.negative(path, original.replace("  ACCEPTANCE EVIDENCE (the bar;", "  REMOVED (the bar;", 1),
                      "tracker needs an acceptance-evidence")
        self.negative(path, original.replace("commit 2e8c45f (main)", "commit missing", 1),
                      "merge artifact needs commit")

    def test_required_artifacts_cannot_be_supplied_by_prose(self):
        path = EXAMPLE_PATHS[0]
        original = self.text(path)
        # Keep every contract word, but remove the R1 contract's delimiters.
        start = original.index("```text\nTASK:")
        end = original.index("\n```", start + 1)
        changed = original[:start] + original[start + 8:end] + original[end + 4:]
        self.negative(path, changed, "expected 1 fenced artifact")

    def test_field_in_another_artifact_does_not_count(self):
        path = EXAMPLE_PATHS[2]
        original = self.text(path)
        changed = original.replace("PRIVACY NOTES:", "REMOVED:", 1)
        changed += "\nPRIVACY NOTES: present in prose, not in the request\n"
        self.negative(path, changed, "field 'PRIVACY NOTES'")

    def test_missing_empty_duplicate_and_unclosed_structures(self):
        path = EXAMPLE_PATHS[2]
        original = self.text(path)
        self.negative(path, original + "\n## 3. The operator's run note\nextra\n",
                      "expected exactly one section")
        changed = re.sub(r"(```text\n)Operator note.*?(\n```)", r"\1\2",
                         original, count=1, flags=re.DOTALL)
        self.negative(path, changed, "empty fenced artifact")
        self.negative(path, original + "\n```text\nunclosed\n", "unclosed code fence")
        for rel in EXAMPLE_PATHS:
            with self.subTest(path=rel):
                source = self.text(rel)
                (self.root / rel).unlink()
                try:
                    self.assertIn(f"{rel}: required example missing or unreadable",
                                  check_worked_examples(str(self.root)))
                finally:
                    self.write(rel, source)

    def test_tilde_fences_and_changed_synthetic_values_are_valid(self):
        for path in EXAMPLE_PATHS:
            self.write(path, self.text(path).replace("```", "~~~~"))
        path = EXAMPLE_PATHS[1]
        self.write(path, self.text(path).replace("210 delivered, 2 bounced",
                                                "0 delivered, 212 bounced"))
        # Deliberately NOT a semantic or cross-artifact consistency checker.
        self.assertEqual(check_worked_examples(str(self.root)), [])

    def test_every_host_request_field(self):
        self.rename_fields(EXAMPLE_PATHS[2], REQUEST_FIELDS)

    def test_host_result_metadata_and_evidence(self):
        path = EXAMPLE_PATHS[2]
        self.rename_fields(path, ("Status", "Ran on", "Build / commit", "Executed by"))
        original = self.text(path)
        self.negative(path, re.sub(r"(?m)^  [0-9a-f]{64}$", "  no-checksum", original),
                      "sha256-shaped")
        self.negative(path, original.replace("  status=UNCONFIRMED reason=observed_version_unchanged",
                                            "  missing-observed-line", 1),
                      "two status/version-or-reason")

    def test_queue_and_ledger_table_shapes(self):
        path = EXAMPLE_PATHS[2]
        original = self.text(path)
        self.negative(path, original.replace("| Head SHA |", "| Removed |", 1),
                      "required columns")
        self.negative(path, original.replace("|---|---|---|---|---|---|---|",
                                            "|---|---|---|---|---|---|", 1),
                      "malformed table separator")
        self.negative(path, original.replace("| DONE | P1 |", "| DONE | |", 1),
                      "needs all 7 cells")
        path = EXAMPLE_PATHS[1]
        self.negative(path, self.text(path).replace("| daily cap used |", "| removed |", 1),
                      "required columns")
        # Empty table and disconnected prose rows must not provide data.
        schema = Schema("fixture")
        header = "| " + " | ".join(QUEUE_COLUMNS) + " |"
        schema.table(header + "\n|---|---|---|---|---|---|---|\n\n"
                     "| a | b | c | d | e | f | g |", QUEUE_COLUMNS, "queue")
        self.assertTrue(schema.failures)

    def test_r3_escalation_decision_and_ledger_fields(self):
        path = EXAMPLE_PATHS[1]
        self.rename_fields(path, ("Decision", "Decided by", "Scope / expiry",
                                 "Supersedes", "Evidence"), 2, bullet=True)
        self.rename_fields(path, ("Authorized by", "Pre-authorized", "Expiry",
                                 "Revocation", "Stop conditions", "Reporting",
                                 "Never covers"))
        self.rename_fields(path, ("WHAT I TRIED",
                                 "EVIDENCE (file@SHA / PR / command output summary)",
                                 "RISK IF IGNORED",
                                 "DECISION NEEDED (bounded options + recommendation)",
                                 "SAFE WORK CONTINUING MEANWHILE"))

    def test_r3_execution_has_labeled_records_not_keywords(self):
        path = EXAMPLE_PATHS[1]
        original = self.text(path)
        for label in ("ATTEMPT", "ACTION", "VERIFIED RESULT"):
            with self.subTest(label=label):
                self.negative(path, original.replace(label + ":", label + " (prose)"),
                              f"labeled '{label}:' record")

    def test_closing_comment_and_post_merge_artifacts(self):
        path = EXAMPLE_PATHS[0]
        original = self.text(path)
        self.negative(path, original.replace("[AGENT] ENG-101 closed.", "ENG-101 closed.", 1),
                      "closing comment must start")
        self.negative(path, original.replace("Unproven: nothing", "Missing: nothing", 1),
                      "closing comment needs 'Unproven:'")
        start = original.index("```text\n- activity-filter helper")
        end = original.index("\n```", start + 1)
        self.negative(path, original[:start] + original[end + 4:], "expected 3 fenced")

    def test_cli_schema_failure_is_third_check_only(self):
        path = EXAMPLE_PATHS[2]
        self.write(path, self.text(path).replace("TEST ID:", "REMOVED:", 1))
        code, output = self.cli()
        self.assertEqual(code, 1, output)
        self.assertIn("PASS: tree matches disk exactly", output)
        self.assertIn("PASS: every checked reference resolves", output)
        self.assertIn("RESULT: FAIL (2/3 checks passed)", output)

    def test_old_tree_check_rejects_added_and_missing_files(self):
        self.write("extra.txt", "synthetic\n")
        code, output = self.cli()
        self.assertEqual(code, 1, output)
        self.assertIn("on disk but missing from the tree: extra.txt", output)
        self.assertIn("RESULT: FAIL (2/3 checks passed)", output)
        (self.root / "extra.txt").unlink()
        (self.root / "LICENSE").unlink()
        code, output = self.cli()
        self.assertEqual(code, 1, output)
        self.assertIn("listed in the tree but not on disk: LICENSE", output)

    def test_old_tree_requires_contents_heading(self):
        self.write("README.md", self.text("README.md").replace("## Repository contents",
                                                            "## Removed", 1))
        code, output = self.cli()
        self.assertEqual(code, 1, output)
        self.assertIn("FAIL: no '## Repository contents' fenced block", output)

    def test_worktree_git_file_is_not_an_unregistered_file(self):
        # Day 2 addendum: in a git worktree, .git is a FILE (gitdir pointer),
        # and it must not be reported as an unregistered repository file.
        (self.root / ".git").write_text("gitdir: /tmp/elsewhere/main/.git\n")
        code, output = self.cli()
        self.assertEqual(code, 0, output)
        self.assertIn("PASS: tree matches disk exactly", output)
        self.assertNotIn(".git", output)

    def test_old_reference_check_rejects_broken_prose_reference(self):
        self.write("README.md", self.text("README.md") + "\nMissing: `docs/absent.md`.\n")
        code, output = self.cli()
        self.assertEqual(code, 1, output)
        self.assertIn("unresolved reference `docs/absent.md`", output)
        self.assertIn("PASS: tree matches disk exactly", output)
        self.assertIn("RESULT: FAIL (2/3 checks passed)", output)

    def test_old_reference_and_tree_exclusions(self):
        self.write("README.md", self.text("README.md") +
                   "\n`human_tests/results/later.md` `PENDING.md` `<file>.md`\n"
                   "```text\n`docs/absent.md`\n```\n")
        for path in (".git/ignored.txt", "__pycache__/ignored.txt", ".venv/ignored.txt",
                     "node_modules/ignored.txt", "sample.log",
                     "human_tests/results/synthetic.md", "docs/agent_handoff/local.md"):
            self.write(path, "synthetic\n")
        code, output = self.cli()
        self.assertEqual(code, 0, output)

    def seed_adopted(self):
        for rel in validate.ADOPTED_RUNTIME_DIRS:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        for rel in validate.ADOPTED_BUNDLE_FILES:
            self.write(rel, "# Synthetic bootstrap output\n")
        self.write(validate.ADOPTED_BUNDLE_DIR + "/decision.md", "# Synthetic decision\n")
        self.write(validate.ADOPTED_PENDING, "# Synthetic requests\n")
        self.write(validate.ADOPTED_HVQ,
                   "## Dated status block — 2026-01-15\n\n| ID | Description |\n")
        self.write("AGENTS.md", "### This project's risk surfaces\n\n"
                   "- R2: verification logic\n- R3: real sends\n")
        self.rehash()

    def rehash(self, binary=False):
        self.write(validate.ADOPTED_MANIFEST, "\n".join(
            hashlib.sha256((self.root / rel).read_bytes()).hexdigest() +
            (" *" if binary else "  ") + rel for rel in validate.MANIFEST_REQUIRED
        ) + "\n")

    def test_adopted_template_still_fails_without_bootstrap(self):
        code, output = self.cli("--adopted")
        self.assertEqual(code, 1, output)
        self.assertIn("RESULT: FAIL (0/6 checks passed)", output)
        self.assertNotIn("Worked-example schemas", output)

    def test_adopted_positive_and_hash_dialects(self):
        self.seed_adopted()
        for binary in (False, True):
            with self.subTest(binary_marker=binary):
                self.rehash(binary)
                code, output = self.cli("--adopted")
                self.assertEqual(code, 0, output)
                self.assertIn("RESULT: PASS (6/6 checks passed)", output)
        # The flag remains a separate mode, not coupled to shipped examples/tree.
        (self.root / EXAMPLE_PATHS[0]).unlink()
        self.write("extra.txt", "synthetic\n")
        code, output = self.cli("--adopted")
        self.assertEqual(code, 0, output)

    def test_each_adopted_gate_negative_remains_isolated(self):
        for gate in range(6):
            with self.subTest(gate=gate + 1):
                self.seed_adopted()
                if gate == 0:
                    (self.root / "agent_reports").rename(self.root / "saved-reports")
                elif gate == 1:
                    self.write(validate.ADOPTED_BUNDLE_DIR + "/decision.md", "")
                elif gate == 2:
                    (self.root / validate.ADOPTED_PENDING).unlink()
                elif gate == 3:
                    self.write(validate.ADOPTED_HVQ,
                               "## Dated status block — [DATE]\n\n| ID | Description |\n")
                    self.rehash()
                elif gate == 4:
                    self.write(validate.ADOPTED_MANIFEST,
                               self.text(validate.ADOPTED_MANIFEST).replace(
                                   self.text(validate.ADOPTED_MANIFEST)[:64], "0" * 64, 1))
                else:
                    self.write("AGENTS.md", self.text("AGENTS.md") + "\n[EDIT ME]\n")
                results = validate.adopted_checks(str(self.root))
                self.assertEqual([passed for _title, passed, _lines in results],
                                 [index != gate for index in range(6)])
                code, output = self.cli("--adopted")
                self.assertEqual(code, 1, output)
                self.assertIn("RESULT: FAIL (5/6 checks passed)", output)

    def test_adopted_manifest_self_entry_still_fails(self):
        self.seed_adopted()
        self.write(validate.ADOPTED_MANIFEST, self.text(validate.ADOPTED_MANIFEST) +
                   "0" * 64 + "  " + validate.ADOPTED_MANIFEST + "\n")
        code, output = self.cli("--adopted")
        self.assertEqual(code, 1, output)
        self.assertIn("MANIFEST.md lists itself", output)

    # --- Privacy scan (scripts/privacy_scan.py) --------------------------

    def privacy_cli(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/privacy_scan.py")],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )
        # Deliberately NOT masking the fixture path in stdout: the
        # scanner must never print an absolute host path itself, and
        # these tests must be able to catch it if it regresses.
        self.assertEqual(result.stderr, "")
        return result.returncode, result.stdout

    def test_privacy_scan_clean_on_the_registered_snapshot(self):
        code, output = self.privacy_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: CLEAN", output)
        self.assertNotIn(str(self.root), output)
        self.assertNotIn("/Users/", output)
        self.assertNotIn("/home/", output)

    def test_privacy_scan_redaction_conceals_short_matches(self):
        # PR #16 review finding 1: even the shortest accepted email shape
        # must never be echoed in full.
        email = "a" + "@" + "b" + ".co"
        probe = self.root / "scratch-probe.md"
        probe.write_text(f"- contact: {email}\n")
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("email address", output)
            self.assertNotIn(email, output)
        finally:
            probe.unlink()

    def test_privacy_scan_redacts_secret_shaped_filenames(self):
        # PR #16 review finding 2: a secret-shaped FILENAME must not leak
        # through the finding's path even when the finding is redacted.
        token = "gh" + "o" + "_" + "7" * 36
        probe = self.root / f"note-{token}.md"
        probe.write_text(f"note\n\ncontains {token} too\n")
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("service-token", output)
            self.assertNotIn(token, output)
        finally:
            probe.unlink()

    def test_privacy_scan_catches_planted_service_tokens(self):
        # Values are assembled at runtime so this suite never ships a
        # literal that the scanner itself would flag.
        plants = [
            "gh" + "p" + "_" + "1" * 36,
            "github_pat_" + "2" * 36,
            "sk" + "-" + "3" * 40,
            "xox" + "b-" + "4" * 24,
            "AKIA" + "5" * 16,
        ]
        for token in plants:
            with self.subTest(prefix=token[:3]):
                probe = self.root / "scratch-probe.md"
                probe.write_text(f"probe note\n\nmentions {token} inline\n")
                try:
                    code, output = self.privacy_cli()
                    self.assertEqual(code, 1, output)
                    self.assertIn("service-token", output)
                    self.assertIn("scratch-probe.md", output)
                    self.assertNotIn(token, output)
                finally:
                    probe.unlink()

    def test_privacy_scan_catches_planted_assignment_and_key_block(self):
        value = "s" * 6 + "e" * 10
        pem = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
        probe = self.root / "scratch-probe.md"
        probe.write_text(
            f"# probe\n\n- token: {value}\n\n```text\n{pem}\nmiI...\n```\n"
        )
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("credential assignment", output)
            self.assertIn("private-key block", output)
            self.assertNotIn(value, output)
        finally:
            probe.unlink()

    def test_privacy_scan_catches_planted_email_and_home_path(self):
        email = "per" + "son@" + "somewhere" + ".org"
        home = "/Users/" + "someuser" + "/notes.txt"
        probe = self.root / "scratch-probe.md"
        probe.write_text(f"- contact: {email}\n- capture: {home}\n")
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("email address", output)
            self.assertIn("absolute home path", output)
            self.assertNotIn(email, output)
            self.assertNotIn(home, output)
        finally:
            probe.unlink()

    def test_privacy_scan_tolerates_documented_placeholders(self):
        probe = self.root / "scratch-probe.md"
        probe.write_text(
            "- token: <value>\n"
            "- API key: [REDACTED]\n"
            "- contact: user@example.com\n"
            "- github bot: 138933559+factory-droid[bot]@users.noreply.github.com\n"
            "- path: /Users/<you>/repo\n"
            '- printf "password=%s" "$value"\n'
        )
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 0, output)
            self.assertIn("RESULT: CLEAN", output)
        finally:
            probe.unlink()

    def test_privacy_scan_includes_runtime_record_directories(self):
        token = "gh" + "r" + "_" + "6" * 36
        probe = self.root / "agent_reports" / "scratch.md"
        probe.write_text(f"day note\n\nsaw {token}\n")
        try:
            code, output = self.privacy_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("service-token", output)
            self.assertIn("agent_reports/scratch.md", output)
        finally:
            probe.unlink()

    # --- Markdown lint (scripts/md_lint.py) -------------------------------

    def md_cli(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/md_lint.py")],
            cwd=self.root, capture_output=True, text=True, timeout=15,
        )
        # Not masking the fixture path: the lint must never print one.
        self.assertEqual(result.stderr, "")
        return result.returncode, result.stdout

    def test_md_lint_clean_on_the_registered_snapshot(self):
        code, output = self.md_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: CLEAN", output)
        self.assertNotIn(str(self.root), output)

    def test_md_lint_flags_each_structural_violation(self):
        violations = {
            "unclosed fenced code block": "# Title\n\n```text\nunclosed\n",
            "heading level jump": "# Title\n\n### Skipped a level\n",
            "trailing whitespace": "# Title\n\n- item with trailing space   \n",
            "missing final newline": "# Title\n\n- no final newline",
            "trailing blank line(s)": "# Title\n\n- ends with blanks\n\n\n",
            "H1 headings (expected 1)": "# One\n\n# Two\n",
            "no H1 heading": "## Only H2\n\nbody\n",
        }
        original = self.text("docs/maturity.md")
        try:
            for diagnostic, snippet in violations.items():
                with self.subTest(diagnostic=diagnostic):
                    self.write("docs/maturity.md", snippet)
                    code, output = self.md_cli()
                    self.assertEqual(code, 1, output)
                    self.assertIn(diagnostic, output)
        finally:
            self.write("docs/maturity.md", original)

    def test_md_lint_agent_reports_may_stack_day_sections(self):
        # Documented exemption: dated records can carry one H1 per day
        # section; the same shape elsewhere fails (see the violation test).
        probe = self.root / "agent_reports" / "scratch-days.md"
        probe.write_text("# Day A\n\n- one\n\n# Day B\n\n- two\n")
        try:
            code, output = self.md_cli()
            self.assertEqual(code, 0, output)
            self.assertIn("RESULT: CLEAN", output)
        finally:
            probe.unlink()

    def test_md_lint_fence_matching_requires_a_matching_closer(self):
        # PR #17 review finding 1: a fence closes only on the same
        # character, at least the same length, with nothing after it.
        original = self.text("docs/maturity.md")
        try:
            for snippet in (
                "# Title\n\n```text\nbody\n~~~\n",       # other character
                "# Title\n\n```text\nbody\n```junk\n",   # trailing text
                "# Title\n\n````\nbody\n```\n",          # shorter run
            ):
                with self.subTest(snippet=snippet):
                    self.write("docs/maturity.md", snippet)
                    code, output = self.md_cli()
                    self.assertEqual(code, 1, output)
                    self.assertIn("unclosed fenced code block", output)
            # A valid four-backtick block may contain three-backtick
            # examples without ending early or inventing prose findings.
            self.write(
                "docs/maturity.md",
                "# Title\n\n````\n```text\nexample\n```\n````\n",
            )
            code, output = self.md_cli()
            self.assertEqual(code, 0, output)
            self.assertIn("RESULT: CLEAN", output)
        finally:
            self.write("docs/maturity.md", original)

    def test_md_lint_requires_an_h1_even_under_agent_reports(self):
        # PR #17 review finding 2: the report exemption covers stacked
        # day headings, not the absence of a title.
        probe = self.root / "agent_reports" / "scratch-headingless.md"
        probe.write_text("body without H1\n")
        try:
            code, output = self.md_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("no H1 heading", output)
        finally:
            probe.unlink()

    def test_md_lint_redacts_secret_shaped_filenames(self):
        # PR #17 review finding 3: a finding must never echo a filename
        # that carries a secret-shaped identifier (the privacy scan
        # cannot see identifiers that live only in a filename).
        token = "gh" + "s" + "_" + "5" * 36
        probe = self.root / f"note-{token}.md"
        probe.write_text("# Title\n\n- trailing space   \n")
        try:
            code, output = self.md_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("trailing whitespace", output)
            self.assertNotIn(token, output)
        finally:
            probe.unlink()

    # --- One-command check runner (scripts/check.py) -----------------------

    def stub_check(self, script, code, message):
        """Replace one sub-check with a fixed-exit stub.

        These tests are about the RUNNER's behavior (aggregation, exit-code
        propagation, error reporting, continuation), not about re-running
        the whole suite: the fixture's own test_validate.py would otherwise
        invoke check.py, which invokes this suite again — unbounded
        recursion. The real sub-checks are exercised by their own tests and
        by the top-level `python3 scripts/check.py` run recorded in the PR
        evidence, so stubbing the inner invocation narrows nothing about
        the runner's contract.
        """
        self.write(script, f"import sys\nprint({message!r})\nsys.exit({code})\n")

    def check_cli(self):
        """Run the runner in the fixture and return its RAW output.

        Deliberately unmasked: a masked capture would make any
        "the path does not appear" assertion vacuous and could hide a real
        output leak (the PR #16/PR #19 lesson).
        """
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/check.py")],
            cwd=self.root, capture_output=True, text=True, timeout=120,
        )
        return result.returncode, result.stdout + result.stderr

    def test_validate_does_not_print_the_absolute_repository_root(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/validate.py")],
            cwd=self.root, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn(str(self.root), result.stdout)
        self.assertNotIn(str(self.root), result.stderr)
        self.assertIn("repo root: (absolute path omitted)", result.stdout)

    def test_check_runner_passes_on_the_registered_snapshot(self):
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        code, output = self.check_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: PASS (4/4 checks passed)", output)
        for label in ("structural self-validation", "validator regressions",
                      "privacy scan", "markdown lint"):
            self.assertIn(label, output)
        # Unmasked assertion: no absolute repository root in the output.
        self.assertNotIn(str(self.root), output)
        self.assertNotIn("Traceback", output)

    def test_check_runner_continues_after_an_early_failure(self):
        # An early failing check must not stop the run: every later check
        # still runs and still reports its own status.
        # The first check (validate.py) is made to fail for real by planting
        # an unregistered file; it cannot be stubbed like the others because
        # every other check imports it as a module.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write("unregistered-extra.md", "# Title\n\nbody\n")
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        self.assertIn("FAIL: structural self-validation", output)
        self.assertIn("PASS: validator regressions", output)
        self.assertIn("PASS: privacy scan", output)
        self.assertIn("PASS: markdown lint", output)
        self.assertIn("RESULT: FAIL (1/4", output)

    def test_check_runner_reports_every_check_in_the_summary(self):
        # Exactly four results, whatever the outcomes: a runner that skips
        # a check after a failure cannot pass this.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write("unregistered-extra.md", "# Title\n\nbody\n")
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        summary = output.split("summary:", 1)[1]
        statuses = re.findall(r"^  (PASS|FAIL|ERROR)\s", summary, flags=re.M)
        self.assertEqual(len(statuses), 4, output)
        self.assertEqual(statuses.count("PASS"), 3, output)
        self.assertEqual(statuses.count("FAIL"), 1, output)

    def test_check_runner_propagates_a_nonzero_sub_check_exit(self):
        # A sub-check that ran and failed for its own reasons fails the run
        # even when nothing else is wrong.
        self.stub_check("scripts/test_validate.py", 3, "stub: three failures")
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        self.assertIn("FAIL: validator regressions", output)
        self.assertIn("RESULT: FAIL (1/4", output)

    def test_check_runner_reports_a_missing_check_as_error(self):
        # A check that cannot run is ERROR, never a silent skip or a pass.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        (self.root / "scripts" / "md_lint.py").unlink()
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        self.assertIn("ERROR: markdown lint", output)
        self.assertIn("RESULT: FAIL", output)
        self.assertNotIn("RESULT: PASS", output)

    def test_check_runner_reports_a_non_file_check_as_error(self):
        # PR #19 review finding 2: a directory where a check should be means
        # the check never ran — ERROR, not FAIL.
        # Stub target note: md_lint.py is a leaf (nothing imports it), so
        # replacing it cannot disturb another check's import.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        target = self.root / "scripts" / "md_lint.py"
        target.unlink()
        target.mkdir()
        try:
            code, output = self.check_cli()
            self.assertEqual(code, 1, output)
            self.assertIn("ERROR: markdown lint", output)
            self.assertIn("not a regular file", output)
        finally:
            shutil.rmtree(target, ignore_errors=True)

    def test_check_runner_reports_an_unreadable_check_as_error(self):
        # os.geteuid is POSIX-only; skip the case where it is absent rather
        # than failing an adopter's suite on Windows.
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        target = self.root / "scripts" / "md_lint.py"
        target.chmod(0o000)
        try:
            code, output = self.check_cli()
        finally:
            target.chmod(0o644)
        self.assertEqual(code, 1, output)
        self.assertIn("ERROR: markdown lint", output)

    def test_check_runner_survives_undecodable_check_output(self):
        # PR #19 review finding 3: invalid bytes must not abort the run or
        # hide the failing check's real exit code.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write(
            "scripts/md_lint.py",
            "import sys\n"
            "sys.stdout.buffer.write(b'\\xff\\xfe invalid')\n"
            "sys.stdout.flush()\n"
            "sys.exit(9)\n",
        )
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        self.assertNotIn("Traceback", output)
        self.assertIn("FAIL: markdown lint", output)
        self.assertIn("PASS: privacy scan", output)
        self.assertIn("RESULT: FAIL (1/4", output)

    def test_check_runner_counts_an_error_as_not_passed_in_the_aggregate(self):
        # PR #19 re-review finding 1: an unrunnable check must fail the run
        # even when every other check passed. Built as a minimal isolated
        # repository (four stubs, one of them unrunnable) so no other
        # check's outcome can mask the aggregate verdict — in the shared
        # fixture an unrunnable script usually breaks another check too,
        # which is what left this case unpinned.
        fake = Path(tempfile.mkdtemp(prefix="mission-runner-"))
        self.addCleanup(shutil.rmtree, fake, True)
        (fake / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts" / "check.py", fake / "scripts" / "check.py")
        for script in ("validate.py", "test_validate.py", "privacy_scan.py"):
            (fake / "scripts" / script).write_text("print('stub: ok')\n")
        (fake / "scripts" / "md_lint.py").mkdir()
        result = subprocess.run(
            [sys.executable, str(fake / "scripts" / "check.py")],
            cwd=fake, capture_output=True, text=True, timeout=60,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertIn("ERROR: markdown lint", output)
        self.assertIn("RESULT: FAIL (1/4 checks did not pass: markdown lint)", output)
        statuses = re.findall(
            r"^  (PASS|FAIL|ERROR)\s", output.split("summary:", 1)[1], flags=re.M
        )
        self.assertEqual(statuses, ["PASS", "PASS", "PASS", "ERROR"], output)
        self.assertNotIn("RESULT: PASS", output)
        self.assertNotIn(str(fake), output)

    def test_check_runner_sanitizes_forwarded_absolute_paths(self):
        # PR #19 review finding 1: a sub-check's output must not print the
        # operator's absolute repository root to the console.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write(
            "scripts/md_lint.py",
            "import os\n"
            "print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n",
        )
        code, output = self.check_cli()
        self.assertEqual(code, 0, output)
        self.assertNotIn(str(self.root), output)
        self.assertIn("<repo root>", output)

    # The next four tests pin runner behavior that cannot be reached through
    # a subprocess from the fixture without waiting 900 seconds or forcing
    # an OS error: the runner is therefore loaded as a module and the one
    # constant or seam under test is replaced. Each asserts the real code
    # path, not a stub of it. Recorded as non-blocking coverage gaps in the
    # PR #19 independent review.

    def load_runner(self):
        """Load the fixture's scripts/check.py as an importable module."""
        spec = importlib.util.spec_from_file_location(
            "check_runner_under_test", self.root / "scripts" / "check.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_check_runner_forwards_stderr_from_a_check(self):
        # A check's stderr is evidence too: dropping it would hide failures
        # that a check reports only there.
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write(
            "scripts/md_lint.py",
            "import sys\n"
            "print('stdout marker')\n"
            "print('stderr marker', file=sys.stderr)\n",
        )
        code, output = self.check_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("stdout marker", output)
        self.assertIn("stderr marker", output)

    def test_check_runner_reports_a_sub_check_exit_code_unchanged(self):
        # The exact code a check exited with must reach the report: a runner
        # that normalised it to 0/1 would hide which check failed how.
        self.stub_check("scripts/test_validate.py", 3, "stub: three failures")
        self.write(
            "scripts/md_lint.py",
            "import sys\nsys.exit(9)\n",
        )
        code, output = self.check_cli()
        self.assertEqual(code, 1, output)
        self.assertIn("validator regressions (exit 3)", output)
        self.assertIn("markdown lint (exit 9)", output)
        self.assertIn("RESULT: FAIL (2/4", output)

    def test_check_runner_sanitizer_covers_both_root_spellings(self):
        # A checkout reached through a symlink has two spellings of its
        # root — the one it was invoked with and the resolved one — and
        # both must be replaced, or the operator's real path leaks.
        # The documented limit (a contrived third spelling) is stated in
        # make_sanitizer's docstring and is not asserted here as covered.
        real = self.root / "real-repo"
        real.mkdir()
        link = self.root / "linked-repo"
        link.symlink_to(real, target_is_directory=True)
        module = self.load_runner()
        sanitize = module.make_sanitizer(str(link))
        resolved = os.path.realpath(str(link))
        self.assertNotIn(str(link), sanitize(f"wrote {link}/scripts/x.py"))
        self.assertNotIn(resolved, sanitize(f"wrote {resolved}/scripts/x.py"))
        self.assertIn("<repo root>/scripts/x.py", sanitize(f"wrote {link}/scripts/x.py"))
        self.assertIn("<repo root>/scripts/x.py", sanitize(f"wrote {resolved}/scripts/x.py"))

    def test_check_runner_reports_a_timed_out_check_as_error(self):
        # The timeout path is otherwise unreachable without waiting 900s.
        module = self.load_runner()
        module.TIMEOUT_SECONDS = 1
        self.stub_check("scripts/test_validate.py", 0, "stub: regressions ok")
        self.write("scripts/slow-stub.py", "import time\ntime.sleep(10)\n")
        sanitize = module.make_sanitizer(str(self.root))
        status, code, output = module.run_check(
            str(self.root), "scripts/slow-stub.py", sanitize
        )
        self.assertEqual(status, "ERROR", output)
        self.assertEqual(code, 124, output)
        self.assertIn("timed out", output)
        self.assertNotIn(str(self.root), output)
        # A timed-out check must not stop the ones after it.
        module.CHECKS = (
            ("slow check", "scripts/slow-stub.py"),
            ("markdown lint", "scripts/md_lint.py"),
        )
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = module.main()
        report = buffer.getvalue()
        self.assertEqual(exit_code, 1, report)
        self.assertIn("ERROR: slow check", report)
        self.assertIn("PASS: markdown lint", report)
        self.assertIn("RESULT: FAIL (1/2 checks did not pass: slow check)", report)

    def test_check_runner_reports_a_start_failure_as_error(self):
        # A check the OS refuses to start never ran: ERROR, and the
        # exception text (which can carry an absolute path) is not printed.
        module = self.load_runner()
        refusal = OSError(13, "Permission denied", str(self.root / "scripts"))
        with mock.patch.object(module.subprocess, "run", side_effect=refusal):
            status, code, output = module.run_check(
                str(self.root), "scripts/md_lint.py", module.make_sanitizer(str(self.root))
            )
        self.assertEqual(status, "ERROR", output)
        self.assertEqual(code, 126, output)
        self.assertIn("could not start", output)
        # The exception's type name is reported; its message (which can
        # carry an absolute path) is not.
        self.assertIn("(PermissionError)", output)
        self.assertNotIn(str(self.root), output)
        self.assertNotIn("Permission denied", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
