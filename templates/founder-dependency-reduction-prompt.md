# Founder-dependency reduction prompt

Run this prompt (with the `human-dependency-audit` skill) when the
Mission's queue accumulates founder-blocked items, or periodically as a
governance review. Its output is a **per-item proposal** — never a bundle
— that the founder approves or rejects item by item. Replace the
bracketed placeholders.

---

You are running a human-dependency audit for this engineering Mission
(skill: `.factory/skills/human-dependency-audit/SKILL.md`). Produce a
founder proposal with three sections, in this order.

## Section 1 — Inventory of waits

Collect every item currently waiting on a human: tracker issues labeled
`needs-founder` or `needs-human`, host validation queue rows, PRs
awaiting founder decision or review, budget requests, and recurring
manual asks. For each, record in a table:

| ID | What the manual action is | Why it exists | Recurs how often | Current label | Proposed label |
|---|---|---|---|---|---|
| [ISSUE-1] | [e.g., "Founder runs the on-device smoke test each release"] | [e.g., "No written operator procedure; trust in executor"] | [e.g., "every release"] | needs-founder | needs-human |

Classify each wait: **needs-machine** (no human required; automate),
**needs-human** (a qualified human, not the founder), **needs-founder**
(R3, budgets/credentials, policy, benchmark/corpus/scoring approval,
merge/release decisions, genuine human-experience validation, irreversible
or privacy-consequential acts). Push items leftward only where evidence
quality is preserved. Say which items you are *not* proposing to move,
and why.

## Section 2 — Per-item reduction proposals

For every proposed change, one self-contained item:

```text
P# — [SHORT NAME] (needs-founder → needs-human | needs-human → needs-machine)

MANUAL ACTION BEFORE: what the founder does today, and why it existed
REPLACEMENT: the mechanism — written operator procedure / bounded
  standing authorization with expiry / one-time bootstrap checklist /
  synthetic test surface / automation on an available host
EVIDENCE QUALITY: EQUAL | STRONGER (+ how the runs, exact-SHA rule,
  status vocabulary, and independent review are unchanged)
  (a WEAKER rating must be explicit, justified, and is usually wrong)
NEW RISKS + MITIGATION: e.g., operator error → verbatim-only rule,
  stop conditions, unchanged independent review
ROLLBACK: how to revoke instantly; what reverts
WHAT STAYS FOUNDER-ONLY: the things this item never touches
GOVERNANCE TEXT CHANGED: exact policy lines that must be amended, with
  proposed wording (none if unchanged)
```

Draw from the delegation toolkit in order of preference: automate on an
available host → delegate to a qualified operator with a written
procedure → bounded standing authorization with expiry and a metered
ledger → one-time bootstrap instead of recurring setup → synthetic
disposable test surfaces → batch irreducibly-human privileged work
(never build privilege-escalation shims).

## Section 3 — What is NOT proposed

List the guardrails explicitly (this section is what makes the proposal
trustworthy):

- No threshold, gate, or benchmark changes; no test deletions.
- No synthetic-for-host substitution; no human-experience proxies where
  the human experience is the requirement.
- No safety-refusal-as-success; no "action sent = goal achieved".
- No removal of independent review; no self-merge authority.
- No privacy or safety policy edits; no hidden capability expansion.
- No post-hoc exclusion of known failures.

## Handling the response

- Present items for **independent approve/reject**; do not treat "yes to
  P1" as "yes to all".
- On approval: record it in the durable decision record (dated addendum),
  apply tracker label changes, create any operator packets or ledger
  entries, and note the expiry date of every standing authorization.
- On rejection: record the reason; the item keeps its current label.
- Track outcomes: founder interruptions per week, evidence-quality
  incidents per delegation. If a delegation produces degraded evidence,
  revoke it — that is the audit working, not failing.

Then continue the Mission's safe parallel work; do not wait idle for the
response.
