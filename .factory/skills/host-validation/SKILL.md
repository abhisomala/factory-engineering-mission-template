---
name: host-validation
description: Request, record, and update host-specific validation queue (HVQ) items. Use when a check can only be certified on a specific host (a real device, OS, browser, or environment), when host evidence has arrived, when an HVQ row must be added or updated, or when a PR's host-evidence bar must be assessed. Never claims target-host evidence from another host, a simulation, or a fixture.
---

# Host validation (HVQ) workflow

Some behaviors can only be certified on a specific host: a real mobile OS,
a particular browser engine, a physical device, a production environment,
or a machine you cannot reach from where you work. That host is an
**intermittent, human-operated worker**. This skill drives the recurring
loop for host-specific evidence: pick a READY item, request it precisely,
record what comes back honestly, and keep the queue current. The queue
file is `docs/agent_handoff/HOST_VALIDATION_QUEUE.md` (read its newest
dated block first).

## 1. Read the queue; never claim host evidence you do not have

- Read the queue end to end before doing anything.
- Absolute rule: **nothing you run on your current host is evidence for a
  different host.** A Linux CI box does not certify macOS behavior; a
  browser automation fixture does not certify a real screen reader;
  synthetic tests never certify real-device behavior.
- Unrun host cases are `UNEXECUTED_ON_<HOST>` — never pass, never fail.
- If host evidence is required for a decision, say so and use this skill
  instead of improvising.

## 2. Pick a READY item with a verified SHA

- Choose the highest-priority READY item (P0 first) whose prerequisites
  you can state exactly (apps running, permissions granted, person at
  keyboard, budget).
- **Re-verify rule:** fetch the PR head's current SHA
  (`git ls-remote origin <branch>`) and compare it with the queue row. If
  the head moved, the row goes back to READY with the new SHA — a PASS at
  an old SHA is history, not evidence for the new head.
- Confirm the item needs no ungranted budget (metered runs need an
  explicit, recorded founder budget first).

## 3. Request it via `human_tests/PENDING.md`

Append a request block (replacing any stale entry for the same test ID):

```text
TEST ID: <HVQ-ID>
REQUESTED BY TASK / PR: <task or PR reference>
REQUIRED ENVIRONMENT: <HOST> (state device/permission/person needs)
BUILD / COMMIT: <exact PR head SHA and branch>
RECORDED REPRODUCER STATUS: UNEXECUTED_ON_<CURRENT-HOST>
WHY THE CURRENT HOST CANNOT CERTIFY IT: <one line>
PREREQUISITES / PERMISSIONS: <apps running, grants, test accounts...>
SAFE STEPS / COMMANDS: <exact commands; fresh clone or worktree only;
  never the operator's dirty working copy; state model-call count and any
  UI mutation; read-only unless the request explicitly authorizes a
  reversible change on a declared test surface>
EXPECTED EVIDENCE: <exact observable results and pass criteria>
PRIVACY NOTES: <what the output contains; no raw private content>
CLEANUP / RESTORE: <what to close or remove afterwards>
RESULT FILE: human_tests/results/<TEST-ID>.md
```

The request must be executable **verbatim** by a qualified operator who is
not an engineer. If a step is not written down, the step does not happen.

## 4. Record results honestly

When the sanitized result comes back:

- Preserve the raw returned material **on the host where it was produced**
  (or your own host, in a dated raw-run directory) and record its checksum
  at the top of the sanitized result file, so the record is verifiable
  without exposing private content.
- Save the sanitized result to `human_tests/results/<TEST-ID>.md`.

Status vocabulary — use exactly one:

- **PASS** — every expected criterion observed at that exact SHA.
- **FINDING** — ran, but something real deviated; record what deviated and
  whether it fails safe.
- **INCOMPLETE** — could not execute fully (missing app, missing
  permission, aborted run). Never a pass; state the missing prerequisite.
- **INCONCLUSIVE** — ran but the measurement is unusable; the run is
  spent; say so honestly.
- **UNEXECUTED_ON_<HOST>** — not run on the required host yet; no
  inference from other hosts.

Apply the result only to the exact tested SHA. If the head moved since,
mark the row READY again at the new SHA.

## 5. Update the queue and the durable context

The queue file (`docs/agent_handoff/HOST_VALIDATION_QUEUE.md`) uses one
table row per item, organized under dated blocks (newest block first):

```markdown
# Host validation queue (durable)

## Dated status block — YYYY-MM-DD (LATEST)
[what changed in this window and why; supersedes older blocks, which stay
as history]

| ID | Description (task/PR, commands, scope) | Status | Priority | Head SHA | Requested | Result |
|---|---|---|---|---|---|---|
| HVQ-01 | Readiness preflight for the validation host | READY | P0 | <sha> | <date> | — |
```

- Row rules: one row per check; never delete or rewrite an old row —
  append a dated status note (statuses: `READY`, `LEASED`, `IN_REVIEW`,
  `PASS`, `FINDING`, `INCOMPLETE`, `INCONCLUSIVE`, `UNEXECUTED_ON_<HOST>`,
  `BLOCKED`, `DONE`).
- `READY` means executable in the next host window; record prerequisites
  in the description or the linked `PENDING.md` block.
- After every head change on a referenced branch, refresh the row's SHA
  and re-verify before trusting any earlier PASS.
- New requests are numbered sequentially (`HVQ-NN`); a check reserved
  exclusively for one task says so in its description.

Queue maintenance with the rest of the durable context:

- Update the HVQ row with a dated status note (keep old text as history).
- Update the durable context manifest and as-of line for any file you
  changed. Dated addenda only.
- Link the queue row to the tracker issue so the founder sees it in the
  queue (see `docs/linear-workflow.md`).

## 6. Escalate without blocking

- If a merge decision waits on the host item, say so with bounded options
  and continue any unrelated safe (R0/R1, non-blocking) work meanwhile.
- **Blocked paths never idle the whole Mission.**
- If a returned result is ambiguous or contradicts expectations, stop using
  it for decisions, record it verbatim, and escalate with the escalation
  template in `docs/architecture.md`.

## Success criteria

A run of this skill ends with: a precise `PENDING.md` request (or an
honestly recorded result at an exact SHA), the queue row updated with a
dated note, the durable context manifest refreshed, the tracker issue
updated, and the founder informed — with **nothing presented as host
evidence that did not come from that host**.
