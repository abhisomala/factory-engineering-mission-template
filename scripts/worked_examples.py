"""Narrow structural schemas for the three shipped, synthetic worked examples.

No commands, artifact paths, authorization claims, or host results in an
example are executed or verified. See docs/worked-example-schema.md.
"""

from __future__ import annotations

import os
import re

EXAMPLE_PATHS = (
    "examples/worked-example.md",
    "examples/worked-r3-example.md",
    "examples/worked-host-validation.md",
)
CONTRACT_FIELDS = (
    "TASK", "WHY NOW / BLOCKING WHAT", "OWNER (worker/session)",
    "REVIEW PATH", "EXECUTION ENVIRONMENT", "RISK TIER", "SCOPE",
    "OUT OF SCOPE", "REQUIRED ARTIFACTS / INPUTS",
    "BASELINE EVIDENCE + PROVENANCE", "HYPOTHESIS", "ACCEPTANCE EVIDENCE",
    "CAN REQUIRED TESTS ACTUALLY RUN ON THIS HOST?",
    "IF NOT, RECORDED CASE + HOST HANDOFF PLAN", "HUMAN / HOST TEST REQUIRED",
    "PRIVACY / DATA IMPACT", "EXTERNAL PROVIDERS / METERED?",
    "ROLLBACK POINT", "TIME / ATTEMPT BUDGET", "STOP / ESCALATION CONDITIONS",
    "SAFE PARALLEL WORK IF BLOCKED",
)
HANDOFF_SECTIONS = (
    "Status", "Task / Branch", "What was built", "Files changed",
    "Exact validation run", "Metrics", "Safety / privacy review",
    "Known limitations", "Assumptions", "Not tested autonomously (and why)",
    "Human validation required", "Merge blockers", "Recommended next action",
)
REVIEW_FIELDS = (
    "evidence exists", "host evidence from host", "no gate regresses",
    "no test/benchmark weakening", "safety/privacy preserved",
    "independent final review", "PR states proven/unproven",
)
REQUEST_FIELDS = (
    "TEST ID", "REQUESTED BY TASK / PR", "REQUIRED ENVIRONMENT",
    "BUILD / COMMIT", "RECORDED REPRODUCER STATUS",
    "WHY THE CURRENT HOST CANNOT CERTIFY IT", "PREREQUISITES / PERMISSIONS",
    "SAFE STEPS / COMMANDS", "EXPECTED EVIDENCE", "PRIVACY NOTES",
    "CLEANUP / RESTORE", "RESULT FILE",
)
QUEUE_COLUMNS = (
    "ID", "Description (task/PR, commands, scope)", "Status", "Priority",
    "Head SHA", "Requested", "Result",
)
LEDGER_COLUMNS = ("date", "purpose", "sha", "sends", "daily cap used", "result file")
FIELD_RE = re.compile(r"^(?:- )?([A-Za-z][A-Za-z0-9 /()_?+.,@-]*):[ \t]*(.*)$")


def markdown_parts(text: str) -> tuple[list[tuple[int, int, str]], list[str], bool]:
    """ATX headings outside fences; fenced bodies; whether a fence is open."""
    headings: list[tuple[int, int, str]] = []
    blocks: list[str] = []
    fence = ""
    body: list[str] = []
    for index, line in enumerate(text.splitlines()):
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) +
                            "{" + str(len(fence)) + r",}\s*", line):
                blocks.append("\n".join(body))
                fence = ""
                body = []
            else:
                body.append(line)
            continue
        opener = re.match(r"^ {0,3}(`{3,}|~{3,})[^`]*$", line)
        if opener:
            fence = opener.group(1)
            continue
        heading = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if heading:
            headings.append((index, len(heading.group(1)), heading.group(2)))
    return headings, blocks, bool(fence)


class Schema:
    """Accumulate path- and artifact-scoped diagnostics, never outcome claims."""

    def __init__(self, path: str):
        self.path = path
        self.failures: list[str] = []

    def require(self, condition: bool, context: str, message: str) -> None:
        if not condition:
            self.failures.append(f"{self.path}: {context}: {message}")

    def section(self, text: str, title: str) -> str:
        headings, _blocks, _open = markdown_parts(text)
        matches = [h for h in headings if re.fullmatch(title, h[2])]
        self.require(len(matches) == 1, title, "expected exactly one section")
        if len(matches) != 1:
            return ""
        start, level, _title = matches[0]
        end = next((i for i, depth, _t in headings if i > start and depth <= level),
                   len(text.splitlines()))
        body = "\n".join(text.splitlines()[start + 1:end])
        self.require(bool(body.strip()), title, "empty section")
        return body

    def blocks(self, text: str, title: str, count: int = 1) -> list[str]:
        section = self.section(text, title)
        _headings, blocks, _open = markdown_parts(section)
        self.require(len(blocks) == count, title,
                     f"expected {count} fenced artifact(s), found {len(blocks)}")
        for block in blocks:
            self.require(bool(block.strip()), title, "empty fenced artifact")
        return blocks

    def fields(self, text: str, labels: tuple[str, ...], context: str) -> None:
        """Required line-anchored labels, each once with a nonempty value.

        Values may continue across lines, ending at the next field label.
        Prose outside this artifact cannot supply missing fields.
        """
        found: dict[str, list[str]] = {}
        current: str | None = None
        for line in text.splitlines():
            match = FIELD_RE.fullmatch(line)
            if match and (match.group(1) in labels or match.group(1).isupper()):
                current = match.group(1)
                found.setdefault(current, []).append(match.group(2))
            elif line.startswith("#"):
                current = None
            elif current is not None:
                found[current][-1] += "\n" + line
        for label in labels:
            values = found.get(label, [])
            self.require(len(values) == 1 and bool(values[0].strip()),
                         context, f"field '{label}' must occur once with a value")

    def table(self, text: str, columns: tuple[str, ...], context: str) -> None:
        tables: list[list[list[str]]] = []
        current: list[list[str]] = []
        for line in text.splitlines():
            if line.startswith("|") and line.endswith("|"):
                cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
                if not current:
                    current = [cells]
                    tables.append(current)
                else:
                    current.append(cells)
            else:
                current = []
        matching = [t for t in tables if tuple(t[0]) == columns]
        self.require(len(matching) == 1, context, "expected one table with required columns")
        if len(matching) != 1:
            return
        rows = matching[0][1:]
        self.require(len(rows) >= 2, context, "table needs a separator and data row")
        if not rows:
            return
        self.require(len(rows[0]) == len(columns) and
                     all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[0]),
                     context, "malformed table separator")
        for index, row in enumerate(rows[1:], start=1):
            self.require(len(row) == len(columns) and all(row),
                         context, f"data row {index} needs all {len(columns)} cells")

    def closing(self, block: str, context: str) -> None:
        self.require(bool(re.match(r"^\[AGENT\] ENG-\d+ closed\.", block)),
                     context, "closing comment must start '[AGENT] ENG-<id> closed.'")
        # Inline labels are part of the existing closing-comment format.
        matches = list(re.finditer(
            r"\b(Changed|Evidence|Risk|Proven|Unproven|Next)(?: → queued)?:", block))
        for label in ("Changed", "Evidence", "Risk", "Proven", "Unproven", "Next"):
            values = [
                block[match.end():matches[index + 1].start()
                      if index + 1 < len(matches) else len(block)].strip()
                for index, match in enumerate(matches) if match.group(1) == label
            ]
            self.require(len(values) == 1 and bool(values[0]), context,
                         f"closing comment needs '{label}:' once with a value")

    def records(self, text: str, title: str) -> None:
        blocks = self.blocks(text, title, 3)
        if blocks:
            self.closing(blocks[0], title)
        for block, name in zip(blocks[1:], ("addendum", "daily report")):
            self.require(bool(re.match(r"^- \S", block)), title,
                         f"{name} must be a nonempty bullet artifact")


def lifecycle(schema: Schema, text: str) -> None:
    for tier in ("R1", "R2"):
        part = schema.section(text, rf"Part [12] — {tier}:.+")
        for block in schema.blocks(part, r"1\. The tracker issue"):
            schema.require(bool(re.match(r"^ENG-\d+ — \S", block)), tier, "missing issue title")
            schema.fields(block, ("State", "Labels", "Body"), f"{tier} tracker")
            schema.require(bool(re.search(r"^  ACCEPTANCE EVIDENCE [^\n]*:\n  - \S",
                                          block, re.MULTILINE)),
                           tier, "tracker needs an acceptance-evidence bullet list")
        for block in schema.blocks(part, r"2\. The task contract \(filled, every field\)"):
            schema.fields(block, CONTRACT_FIELDS, f"{tier} contract")
        for block in schema.blocks(part, r"3\. The worker handoff(?: \(excerpt\))?"):
            schema.require(block.startswith("# HANDOFF\n"), tier, "missing HANDOFF title")
            for title in HANDOFF_SECTIONS:
                schema.section(block, re.escape(title))
            branch = schema.section(block, "Task / Branch")
            schema.fields(branch, ("Task/issue", "Branch", "Worktree",
                                  "Base commit (exact SHA)", "Head commit (exact SHA)"),
                          f"{tier} handoff branch")
        merge_title = r"4\. The merge" if tier == "R1" else r"5\. The conditional merge"
        for block in schema.blocks(part, merge_title):
            schema.require(bool(re.match(r"^commit [0-9a-f]{7,40} \(main\)\n"
                                         r"Merge pull request #\d+ from \S+", block)),
                           tier, "merge artifact needs commit and PR headers")
        schema.records(part, r"[56]\. Post-merge records \(one comment, one addendum, one report line\)")
        if tier == "R2":
            for block in schema.blocks(part, r"4\. The independent review \(all seven conditions\)"):
                schema.require(block.startswith("INDEPENDENT REVIEW ("), tier,
                               "missing review header")
                for index, label in enumerate(REVIEW_FIELDS, start=1):
                    matches = re.findall(r"^" + str(index) + " " + re.escape(label) +
                                         r":\s*(PASS|FAIL) —[ \t]*(\S[^\n]*)",
                                         block, re.MULTILINE)
                    schema.require(len(matches) == 1, "R2 review",
                                   f"condition {index} needs a status and evidence text")
                schema.fields(block, ("VERDICT", "Next"), "R2 review")
                schema.require(bool(re.search(r"^VERDICT: (APPROVE|FIX-REQUIRED|"
                                              r"WAITING_FOR_REVIEW)$", block, re.MULTILINE)),
                               "R2 review", "invalid verdict vocabulary")


def authorization(schema: Schema, text: str) -> None:
    for block in schema.blocks(text, r"The escalation \(posted once, exactly the template's block\)"):
        schema.require(block.startswith("[AGENT] BLOCKER:"), "R3 escalation",
                       "must start '[AGENT] BLOCKER:'")
        schema.fields(block.removeprefix("[AGENT] "),
                      ("BLOCKER", "WHAT I TRIED",
                       "EVIDENCE (file@SHA / PR / command output summary)",
                       "RISK IF IGNORED",
                       "DECISION NEEDED (bounded options + recommendation)",
                       "SAFE WORK CONTINUING MEANWHILE"), "R3 escalation")
    for block in schema.blocks(text, r"The founder's decision \(dated decision-record entries\)"):
        for title in (r"\d{4}-\d{2}-\d{2} — Standing authorization .+",
                      r"\d{4}-\d{2}-\d{2} — R3 authorization:.+"):
            decision = schema.section(block, title)
            schema.fields(decision, ("Decision", "Decided by", "Scope / expiry",
                                     "Supersedes", "Evidence"), "R3 decision")
    for block in schema.blocks(text, "The standing-authorization ledger entry"):
        schema.fields(block, ("Authorized by", "Pre-authorized", "Expiry",
                              "Revocation", "Stop conditions", "Reporting",
                              "Never covers"), "R3 ledger")
        schema.table(block, LEDGER_COLUMNS, "R3 metered ledger")
    blocks = schema.blocks(text, r"Execution under the grant \(attempt ≠ action ≠ verified result\)", 2)
    if blocks:
        for label in ("ATTEMPT", "ACTION", "VERIFIED RESULT"):
            schema.require(bool(re.search(r"(?:^\s*(?:\d{2}:\d{2}\s+)?|\. )" +
                                          label + r":\s*\S", blocks[0], re.MULTILINE)),
                           "R3 execution", f"needs a labeled '{label}:' record")
        schema.require(bool(re.match(r"^\d{2}:\d{2}  \S", blocks[0])),
                       "R3 execution", "needs timestamped execution records")
    if len(blocks) == 2:
        schema.closing(blocks[1], "R3 execution")


def host_validation(schema: Schema, text: str) -> None:
    for block in schema.blocks(text, r"1\. The queue rows \(schema §5\)"):
        dated = schema.section(block, r"Dated status block — \d{4}-\d{2}-\d{2} \(LATEST\)")
        schema.table(dated, QUEUE_COLUMNS, "host queue")
    for block in schema.blocks(text, r"2\. The request block \(.+\)"):
        schema.fields(block, REQUEST_FIELDS, "host request")
    schema.blocks(text, r"3\. The operator's run note")
    for block in schema.blocks(text, r"4\. The sanitized result file \(.+\)"):
        schema.fields(block, ("Status", "Ran on", "Build / commit", "Executed by"),
                      "host result")
        schema.require(bool(re.search(r"^  [0-9a-f]{64}$", block, re.MULTILINE)),
                       "host result", "needs a raw-capture sha256-shaped value")
        for title in (r"Observed evidence \(.+\)", "Pass criteria check", "Notes"):
            schema.section(block, title)
        observed = schema.section(block, r"Observed evidence \(.+\)")
        schema.require(len(re.findall(r"^  status=[A-Z_]+ (?:observed_version|reason)=\S+$",
                                      observed, re.MULTILINE)) >= 2,
                       "host result", "needs two status/version-or-reason evidence lines")
    schema.records(text, r"5\. Recording it: queue transition and tracker close")


def check_worked_examples(root: str) -> list[str]:
    """Check required artifacts in all three files; paths inside are illustrative."""
    failures: list[str] = []
    for path, check in zip(EXAMPLE_PATHS, (lifecycle, authorization, host_validation)):
        schema = Schema(path)
        try:
            with open(os.path.join(root, path), encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeError):
            failures.append(f"{path}: required example missing or unreadable")
            continue
        schema.require(not markdown_parts(text)[2], "document", "unclosed code fence")
        check(schema, text)
        failures.extend(schema.failures)
    return failures
