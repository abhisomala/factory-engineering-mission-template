# Task contract

Write this contract **before** starting any substantial task. It is the
review anchor: acceptance evidence is judged against what the contract
declared, not against what was convenient to produce. Keep it in the
tracker issue or link it from there.

```text
TASK:
[one sentence — the bounded deliverable]

WHY NOW / BLOCKING WHAT:
[the unmet gate, user problem, or blocked item this addresses]

OWNER (worker/session):
[who executes this task]

REVIEW PATH:
[independent review required (R2) / founder authorization required (R3) /
 autonomous (R0–R1) — who must review before merge]

EXECUTION ENVIRONMENT:
HOST-AGNOSTIC / <TARGET-HOST> / HUMAN-ONLY

RISK TIER:
R0 / R1 / R2 / R3   (docs/risk-model.md; when in doubt, classify up)

SCOPE:
[files/surfaces to touch]

OUT OF SCOPE:
[explicitly excluded; scope creep goes to a new task]

REQUIRED ARTIFACTS / INPUTS:
[specs, fixtures, baseline files — with their provenance; if a required
input is missing, untracked, or private-unsafe: STOP, record which, and
escalate; never substitute a convenient path for a recorded one]

BASELINE EVIDENCE + PROVENANCE:
[what "before" looks like, measured where, at which SHA]

HYPOTHESIS:
[falsifiable — what you expect the change to do and how it can be
proven wrong]

ACCEPTANCE EVIDENCE:
[the exact artifacts that prove completion: tests to pass, gates, host
results, numbers with numerators/denominators — and on which host]

CAN REQUIRED TESTS ACTUALLY RUN ON THIS HOST?: yes / no / partial
IF NOT, RECORDED CASE + HOST HANDOFF PLAN:
[recorded input + expected output labeled UNEXECUTED_ON_<HOST>, plus the
queue request that will certify it]

HUMAN / HOST TEST REQUIRED:
[yes/no; if yes, which HVQ item and its prerequisites]

PRIVACY / DATA IMPACT:
[what data the change touches, logs, or sends; anything new leaving the
machine is R2 minimum]

EXTERNAL PROVIDERS / METERED?:
[provider, account, expected call volume, budget status — unknown budget
means the metered run does not start]

ROLLBACK POINT:
[branch/commit to return to; how to undo safely]

TIME / ATTEMPT BUDGET:
[e.g., one focused work cycle; ≤3 substantive attempts before writing
the root cause instead of thrashing]

STOP / ESCALATION CONDITIONS:
[what makes you stop this task and escalate instead of pushing through]

SAFE PARALLEL WORK IF BLOCKED:
[R0/non-conflicting work to continue meanwhile — the Mission never idles]
```

## Completion rule

A task is complete only when its **acceptance evidence exists** — as
artifacts, at an exact SHA, on the declared host. "Code written" is not
an exit criterion. Close the task by updating the contract with what was
proven, what was unproven, and what was blocked, then hand off
(`templates/worker-handoff.md`).
