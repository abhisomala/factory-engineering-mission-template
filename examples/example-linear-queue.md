# Example: the tracker queue in practice

A worked example of a Linear (or any tracker) queue under this template,
showing labels, states, and a validation request flowing through it. All
content is generic; replace with your project's real work.

## The board at a glance

| Issue | Title | State | Labels | Who/what unblocks |
|---|---|---|---|---|
| ENG-42 | Ship notification-summary v2 | In Progress | R1 | — (worker owns it) |
| ENG-43 | Verify summary correctness on the real mail client | Blocked | R2, `needs-macos` | host validation window |
| ENG-44 | Regression: summary truncated at 500 chars | In Review | R2 | independent reviewer |
| ENG-45 | Write operator runbook for the device lab | Todo | R0, `needs-machine` | worker assignment |
| ENG-46 | Approve budget for one accuracy re-measure | Blocked | R3, `needs-founder`, `metered` | founder |
| ENG-47 | Usability session with screen-reader users | Blocked | `needs-human`, `needs-founder` | founder + operator |

Reading the board the way the orchestrator does:

- ENG-42 proceeds; nothing waits on a human.
- ENG-43 is a host-evidence item: it has an HVQ row
  (`HOST_VALIDATION_QUEUE.md`) and a pending request block in
  `human_tests/PENDING.md`; when the next device-lab window happens, the
  operator runs it verbatim. The Mission does not idle: other items
  continue.
- ENG-44 is at the independent reviewer (a different worker than the
  author), running the 7-condition checklist.
- ENG-45 is mislabeled as human work — a machine can write the runbook;
  the orchestrator reassigns it. (This is the human-dependency audit
  pushing items leftward.)
- ENG-46 is a genuine founder decision: a metered run needs a budget
  with a hard cap, and only the founder grants budgets.
- ENG-47 is human-experience validation: an operator can run the
  session, the founder approves and conducts it; a simulation can never
  substitute.

## A validation request moving through the queue

**1. Worker discovers the boundary.** The worker implements the summary
feature (ENG-42) and its fixture tests pass on CI. But correctness on
the real mail client can only be certified on a Mac with the client
installed — CI is Linux. It records the reproducer as
`UNEXECUTED_ON_MACOS`, not as a failure, and finishes its handoff.

**2. Orchestrator queues the host item.** It adds HVQ-12 to
`docs/agent_handoff/HOST_VALIDATION_QUEUE.md` (READY, P1, exact head
SHA), writes the request block into `human_tests/PENDING.md` (prereqs:
mail client signed into the test account; steps: three verbatim
commands; expected evidence: the exact truncated-output check; privacy:
subjects prefixed `TEST-`), and links it to ENG-43.

**3. The queue entry looks like this** (one row per check, inside the
current dated block):

```markdown
| HVQ-12 | Mail-client summary correctness (ENG-43); 3 read-only commands, no model calls | READY | P1 | head <sha> | requested <date> | result: — |
```

**4. The operator (or founder) runs it.** In the next host window, the
operator follows the block verbatim, hits the stop condition "output
mentions an unexpected private address", stops, and reports
`INCOMPLETE` with what was missing. Not a pass, not a failure — an
honest incomplete result at an exact SHA.

**5. The orchestrator records and routes.** `INCOMPLETE` result saved to
`human_tests/results/HVQ-12.md`; HVQ-12 row updated with a dated note
and back to READY (with a fresh SHA check — the head may have moved);
ENG-43 comment updated with `[AGENT]` prefix: changed, evidence, risk,
proven/unproven, next action. The founder sees one comment, decides
whether to adjust the request, and the Mission kept working the whole
time.

**6. Evidence quality held constant.** Same commands, same exact-SHA
rule, same status vocabulary, same independent review — only *who
executed* changed (founder → operator). That is what a valid delegation
looks like.

## Escalation comment on a blocked issue

```text
[AGENT] BLOCKER: ENG-46 accuracy re-measure needs a budget before it can run.
WHAT I TRIED: ran the free fixture subset (10/60 cases) — enough to plan, not to certify.
EVIDENCE: fixtures/results@<sha> — 10/10 fixture cases pass; live accuracy unknown.
RISK IF IGNORED: release notes would claim an accuracy number no run has measured.
DECISION NEEDED: (A, recommended) authorize one capped run, 60 calls, hard cap 65, abort on first error; (B) defer the claim from release notes; (C) ship with "unmeasured" label.
SAFE WORK CONTINUING MEANWHILE: ENG-45 operator runbook (R0).
```

One screen, bounded options, a recommendation, and the Mission visibly
not waiting.
