# Mission approval prompt

Use this prompt when a worker or reviewer needs one bounded decision
from the founder. It exists to make human decisions cheap: one screen,
bounded options, a recommendation, and an explicit record of what
happens after approval. Replace the bracketed placeholders.

---

[AGENT] needs one decision. Nothing is blocked while waiting: safe work
continues on [SAFE-WORK-CONTINUING].

## Decision request

**Item:** [WHAT THE DECISION IS ABOUT — one sentence]

**Why now:** [WHAT IT UNBLOCKS / WHAT IT BLOCKS, with the risk if
ignored]

**What I tried first:** [THE AGENTS' INVESTIGATION SO FAR, with evidence
pointers (`file@SHA`, PR, command output)]

**Evidence:**

- [EVIDENCE 1 — artifact pointer + one-line summary]
- [EVIDENCE 2 — ...]

**Risk tier of the affected work:** [R0/R1/R2/R3 + why]

## Options

| Option | What it means | Tradeoff |
|---|---|---|
| **A (recommended): [NAME]** | [EXACT SCOPE OF A] | [WHAT IT COSTS / RISKS / WHY IT'S THE RECOMMENDATION] |
| B: [NAME] | [EXACT SCOPE OF B] | [TRADEOFF] |
| C: Defer | No change now | [WHAT STAYS BLOCKED AND FOR HOW LONG] |

**Recommendation:** A — [ONE-SENTENCE REASON GROUNDED IN THE EVIDENCE]

## If approved, exactly this happens next

1. [STEP 1 — e.g., "the branch is merged under conditional R2 rules
   after the independent-review checklist records APPROVE"]
2. [STEP 2 — e.g., "the host validation request HVQ-07 is queued in
   `human_tests/PENDING.md` for the next host window"]
3. [STEP 3 — e.g., "the decision is recorded in the durable decision
   record with today's date and applied to tracker labels"]

No step outside this list is taken. If any condition changes (head SHA
moves, evidence becomes invalid), the approval does **not** carry over:
I re-ask.

## Standing-authorization variant (only if the decision grants one)

Scope: [EXACT PROCEDURE/SURFACE]. Stop conditions: [ANY DEVIATION, ANY
PROMPT, ANY UNEXPECTED CONTENT → STOP AND REPORT]. Reporting: [ONE
RESULT FILE PER USE / LEDGER REPORTED PER RUN]. Expiry: [DATE]. Renewal:
one word. Revocation: [ONE COMMAND/MESSAGE]. This grant does not expand:
[NAME THE THINGS IT MUST NEVER TOUCH — e.g., R3 actions, budget
expansion, bar changes].

---

Rules for the agent using this template:

- One decision per prompt. Bundled decisions get partially approved and
  partially forgotten; itemize them instead.
- Options must be genuinely bounded and mutually exclusive. The
  recommendation must follow from the evidence shown, not from
  preference.
- Record the founder's answer (including a rejection and its reason) in
  the durable decision record as a dated addendum, and update the
  tracker.
- If the decision would change a standing policy, a risk-tier boundary,
  or a benchmark/scoring rule, say so explicitly in the request — those
  decisions do not generalize from a single approval.
- An unspent authorized budget is recorded `UNSPENT / DEFERRED` and is
  never silently repurposed.
