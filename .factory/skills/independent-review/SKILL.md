---
name: independent-review
description: Independent review checklist for high-risk (R2) changes before merge. Use when a change touching verification, safety, confirmation, privacy, credentials, telemetry, or any test/gate/benchmark is ready for review or a conditional merge is proposed. Produces APPROVE / FIX-REQUIRED / WAITING_FOR_REVIEW with concrete evidence per condition. The final review must be independent of the authoring worker.
---

# Independent review (conditional merge gate for high-risk work)

A high-risk change may be merged only when every condition below holds
concretely. This skill is the review that verifies each one. **If you
authored the change, you may run this checklist, but condition 6
(independence) fails unless a different worker, session, or the founder
performs the final review.**

Why this exists: the agents that implement a change are the least
trustworthy reviewers of it, and the failure mode that matters most — a
change that quietly weakens what "done" means — is invisible unless
someone re-derives the evidence from scratch.

## Inputs to gather first

- PR number, head SHA (re-verify with `git ls-remote origin <branch>`),
  base, and the full diff.
- The PR's own statement of what is and is not proven.
- The affected rows in the host validation queue
  (`docs/agent_handoff/HOST_VALIDATION_QUEUE.md`) and any
  `human_tests/results/` files.
- Prior review comments on the PR (evidence only).

## The 7 conditions, with concrete verification steps

**1. Required evidence exists.**
- List what evidence this change class requires (offline tests, A/B gate
  comparison, live host probe, human-run check, budgeted metered run).
- For each: locate the actual artifact (test output, result file, log with
  checksum). Missing artifact → condition fails.
- **An assertion without an artifact is not evidence.**

**2. Required host evidence actually came from the required host.**
- Trace every host-specific claim to its source: a result file recorded in
  `human_tests/results/` from a run executed on that host, at the same
  head SHA being merged.
- Anything traced to a different host, a simulation, or a fixture →
  condition fails, regardless of how green it looks.
- Apply the re-verify rule: a PASS at an older SHA is history, not
  evidence for the current head.

**3. No passing gate regresses.**
- Run the repository's test suite at the PR head and at base on the same
  host; compare results test-by-test; record the pass/fail list.
- A gate that passed at base and fails at head → condition fails (or the
  behavior change is explicitly re-reviewed as intended).
- Where a host-specific gate cannot run on this host, record
  `UNEXECUTED_ON_<HOST>` and confirm which host evidence covers it.

**4. Tests and benchmarks were not weakened.**
- Read the full diff for: deleted, skipped, or relaxed assertions; changed
  expected outputs; lowered thresholds; removed hard cases; broadened
  allowlists; phrase or example hacks that fit the benchmark instead of
  the general behavior; sleeps replacing real checks; commented-out
  coverage.
- Any bar-lowering that is not itself the reviewed purpose of the change
  (with its own evidence) → condition fails.
- **Changed test assertions get extra scrutiny**: when high-risk behavior
  is involved, an assertion change must be justified by a written reason
  and, where possible, demonstrated against a known-failing case that the
  new assertion still catches.

**5. Safety and privacy boundaries are preserved.**
- Re-run the safety/privacy tests that exist for the touched surface and
  confirm they pass at head.
- Check the diff for new egress paths, credential handling, log fields,
  payload content, or loosened refusals. Anything that widens what leaves
  the machine or weakens a refusal → condition fails.

**6. The final review is independent of the authoring worker.**
- Record who authored and who reviews (worker identity/session).
- Same worker without a materially separate review context → condition
  fails; the verdict becomes `WAITING_FOR_REVIEW` with the checklist
  attached.
- Independent review = a different worker, or the founder.

**7. The PR accurately states what is and is not proven.**
- Compare the PR's claims against the artifacts from conditions 1–5.
  Every claim must be traceable; unproven areas must be labeled unproven
  with their host labels.
- Overclaiming or silent omission ("tested" without host and SHA) →
  condition fails; the PR text itself must be corrected and re-checked.

## Verdict

- **APPROVE** — all 7 verified, evidence listed per condition. Record head
  SHA, reviewer identity, per-condition artifacts, and date. The merge may
  proceed under the conditional policy.
- **FIX-REQUIRED** — any condition fails on the change itself. List each
  failure with exact evidence and the minimal fix; do not merge; re-run
  this checklist after fixes at the new head SHA.
- **WAITING_FOR_REVIEW** — the change is sound but independence or host
  evidence is pending. Queue the missing item (a host-validation request
  or an independent reviewer) and continue other safe work.

## Stop rule for out-of-scope risk

If the review uncovers that the change actually performs, enables, or
prepares an R3 action (real external side effect: send, delete, purchase,
account change, release, visibility, privacy expansion) without explicit
prior authorization: stop the review path immediately, record the
finding, escalate to the founder, and do not merge under any
circumstances. R3 is never satisfied by review; it requires explicit prior
authorization.

## Output format

```text
INDEPENDENT REVIEW (date, reviewer identity, PR #, head SHA)
1 evidence exists:            PASS/FAIL — <artifacts>
2 host evidence from host:    PASS/FAIL — <trace>
3 no gate regresses:          PASS/FAIL — <A/B list>
4 no test/benchmark weakening: PASS/FAIL — <diff findings>
5 safety/privacy preserved:   PASS/FAIL — <tests run>
6 independent final review:   PASS/FAIL — <who authored / who reviewed>
7 PR states proven/unproven:  PASS/FAIL — <corrections needed>
VERDICT: APPROVE / FIX-REQUIRED / WAITING_FOR_REVIEW
Next: <one concrete action>
```

Record the completed checklist in the durable context (dated note on the
PR or task entry) so every merge decision is auditable.
