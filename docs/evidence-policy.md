# Evidence policy

This document defines what counts as proof in the Mission. Its core
claim: **a task is complete only when its evidence exists.** "Code
written" is not an exit criterion, a green checkmark is not a host
result, and a successful attempt is not a verified goal.

## Proven / unproven / blocked

Every report, PR body, and task record separates three things:

- **PROVEN** — backed by an artifact that exists at a stated commit SHA:
  a test output, a recorded result file, a sanitized host result, a
  checksummed log. The artifact, host, SHA, and date are named.
- **UNPROVEN** — believed, intended, or plausible, but without an
  artifact. Saying it is fine; implying it is proven is a violation.
- **BLOCKED** — cannot proceed without something external (a host, a
  budget, a decision, a human). Blocked items are queued with their
  unblocking condition and **never idle the rest of the Mission**.

A PR that hides an unproven area has failed review regardless of what
its tests show.

## Execution success is not goal completion

Three facts are always kept separate:

1. **Attempt** — the system tried to act.
2. **Action** — the action executed (API returned, button pressed,
   process exited 0).
3. **Verified result** — independent evidence shows the intended state
   change actually happened.

A successful action without verification is reported `UNCONFIRMED`, not
as success. **A truthful `UNCONFIRMED` always beats a false `CONFIRMED`;
false confirmation is a red line.** If verification is impossible on the
current host, say so and queue the host check.

## Status vocabulary (use exactly one)

For task/work items:

- `CONFIRMED` — completed and verified.
- `UNCONFIRMED` — attempted; verification failed or was unavailable.
- `UNSUPPORTED` — no available capability fulfills the request.
- `UNAVAILABLE` — the capability exists but current state cannot use it.
- `BLOCKED` — policy, confirmation, or safety prevents execution.
- `FAILED` — the executor explicitly failed.
- `ALREADY` — the goal state already held.

For host/human test results:

- `PASS` — every expected criterion observed at that exact SHA.
- `FINDING` — ran; something real deviated (record what, and whether it
  fails safe).
- `INCOMPLETE` — could not execute fully; never a pass.
- `INCONCLUSIVE` — ran; measurement unusable; the run is spent.
- `UNEXECUTED_ON_<HOST>` — not run on the required host; **never pass or
  fail**, and no inference from other hosts.

For queue items: `READY`, `LEASED`, `IN_REVIEW`, `BLOCKED`,
`NEEDS_MACHINE`, `NEEDS_HUMAN`, `NEEDS_FOUNDER`, `DONE`.

## Host honesty

- Evidence certifies only the host, build, and SHA it was produced on. A
  result at an old SHA is history, not evidence for a new head — re-verify
  the SHA before using it.
- Synthetic tests and fixtures never certify host behavior. CI on one OS
  never certifies another OS. A browser automation fixture never
  certifies assistive-technology behavior.
- CI is optional in this model and any provider works: what matters is
  that a run is labeled with the host it executed on. The loop runs fine
  on locally-executed test runs; where this template says "the
  repository's test suite", that means the project's own tests run on
  the working host — CI is a convenience that widens coverage, never a
  substitute for required-host evidence.
- Host-specific evidence flows one way: the agent writes a precise
  request into `human_tests/PENDING.md`; a qualified human (the founder
  or an authorized operator) executes it on the required host and
  returns **sanitized** results to `human_tests/results/<id>.md`. See
  `.factory/skills/host-validation/SKILL.md`.

## Sanitization (what evidence may contain)

Sanitized evidence is safe for the repository's confirmed visibility.
Before anything enters the repo, remove or generalize: private message
bodies, contact names and addresses, private calendar or document titles,
personal filenames and paths, usernames, secrets and tokens, sensitive
URLs and query strings, screenshots and blobs, and unrelated user
content. Keep only the structural evidence needed to judge the test. Raw
private artifacts stay on the host where they were produced (checksummed
there if they must be referenced).

## Never weaken a bar to get a pass

The following are red lines, not judgment calls:

- deleting or skipping hard cases;
- rewriting expected outputs after seeing actual outputs;
- lowering thresholds, broadening allowlists, or relaxing assertions
  without an independent-review justification;
- adding phrase- or example-specific hacks that fit the benchmark instead
  of the general behavior;
- replacing real checks with sleeps or stubs that always pass;
- reducing denominators, quietly excluding known failures, or counting
  aborted runs as passing.

If a gate or benchmark appears wrong, **stop and document the conflict
with evidence**; escalate if needed. The fix is a reviewed change to the
bar with its own justification, never a quiet edit.

## Benchmark integrity

Maintain three sets:

- **Development set** — may guide implementation freely.
- **Regression set** — known failures converted into durable tests;
  never edited to pass.
- **Sealed holdout** — excluded from tuning until evaluation. If a
  holdout case is ever used to fix behavior, it becomes regression data
  and must be replaced. Never call a tuned set held-out.

Every benchmark report includes: numerator/denominator, commit SHA,
benchmark version, date, environment, known invalid rows, and red-line
counts. **Any new run is a NEW run** — it never re-confirms an old
number, and old unrunnable configurations are not silently equated to new
ones.

## Attempt discipline

For a new gate: run it once for the expected failure when the spec asks
for it. Use at most **3 substantive implementation attempts** per task
unless explicitly authorized for a narrow extra attempt. If still
failing, write the root-cause analysis instead of thrashing, and either
escalate or move to the next safe item.

## The task contract

Every substantial task is written down **before** work starts
(`templates/task-contract.md`): owner (the worker/session), risk tier,
execution environment,
scope, out-of-scope, baseline evidence and its provenance, hypothesis,
acceptance evidence, whether required tests can actually run on this
host (and the host handoff plan if not), rollback point, time/attempt
budget, stop conditions, and the safe parallel work if blocked. The
contract is the review anchor: acceptance evidence is judged against what
the contract declared, not against what was convenient to produce.
