# Tracker issue body

The canonical shape of a task, blocker, validation request, or decision
issue in the project tracker (Linear in this template). Paste the block
below into the issue body. The tracker is the active execution queue;
GitHub stays the truth for code, PRs, and evidence
(`docs/linear-workflow.md`).

```text
TITLE: [AGENT] <verb phrase — one bounded deliverable>

TASK:
[one sentence: the deliverable, not the activity]

WHY NOW / BLOCKING WHAT:
[the unmet gate, user problem, or blocked item this addresses]

RISK TIER:
R0 / R1 / R2 / R3  (docs/risk-model.md — when in doubt, classify up)

DEPENDENCY LABEL:
needs-machine / needs-human / needs-founder   (+ needs-<host>, metered)

EXECUTION ENVIRONMENT:
HOST-AGNOSTIC / <TARGET-HOST> / HUMAN-ONLY

OWNER:
[worker/session — one writer per production surface]

CONTRACT:
[inline the task contract (templates/task-contract.md) or link it;
 every task issue carries one]

ACCEPTANCE EVIDENCE:
[the exact artifact that proves completion, and on which host —
 "implement X" without an evidence bar is not a ready task]

STATE:
Todo (READY) -> In Progress (LEASED) -> In Review -> Done;
Blocked is first-class and always names its unblocking condition

STOP / ESCALATION CONDITIONS:
[what makes the owner stop and escalate instead of pushing through]

SAFE PARALLEL WORK IF BLOCKED:
[the R0 or non-conflicting item to continue meanwhile]

LINKED ARTIFACTS:
[PRs, branches, sanitized result files under human_tests/results/,
 durable-context addenda — by URL or path@SHA]
```

## Rules that make the shape work

- **Everything is an issue.** A task, blocker, validation request, or
  decision that is not in the tracker does not exist; workers keep no
  private side queues.
- **One issue = one bounded task.** Big work becomes an epic with
  worker-sized children, each carrying its own contract and evidence
  bar.
- **The contract is attached, not implied.** The reviewer judges
  acceptance against the contract declared before the work, not against
  what was convenient to produce.
- **Evidence closes the issue.** Close with a pointer to the artifact at
  an exact SHA (`docs/evidence-policy.md`), never with a bare "done".
- **Labels decide who can unblock.** Keep `needs-founder` short and
  audited (`.factory/skills/human-dependency-audit/SKILL.md`).
- **Agent comments are prefixed `[AGENT]`** and state what changed, the
  evidence, the risk, proven vs. unproven, and the next action — no
  routine-progress spam.
