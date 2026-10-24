#!/usr/bin/env python3
"""Repeatable, offline validator regressions in disposable synthetic copies."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
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
        output = result.stdout.replace(str(self.root), "<fixture>")
        self.assertEqual(result.stderr.replace(str(self.root), "<fixture>"), "")
        return result.returncode, output

    def test_privacy_scan_clean_on_the_registered_snapshot(self):
        code, output = self.privacy_cli()
        self.assertEqual(code, 0, output)
        self.assertIn("RESULT: CLEAN", output)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
