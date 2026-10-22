# Worker handoff

A worker writes this handoff before stopping — at a planned checkpoint,
before a usage limit, when blocked, or when handing the surface to a
reviewer or the next worker. A handoff is not optional just because the
checkpoint is small. The reader may be a reviewer, a fresh worker, or a
human: write for someone who was not present.

```text
# HANDOFF

## Status
NOT STARTED | IN PROGRESS | OFFLINE COMPLETE | WAITING_FOR_REVIEW |
HUMAN VALIDATION REQUIRED | BLOCKED

## Task / Branch
- Task/issue:
- Branch:
- Worktree:
- Base commit (exact SHA):
- Head commit (exact SHA):

## What was built
- [what actually changed; one bullet per surface]

## Files changed
- [staged-by-name list]

## Exact validation run
[commands and their exact real outputs — pasted, not summarized;
include the full pass/fail counts and the SHA they were run at]

## Metrics
[numerators/denominators where any measurement occurred; environment
labels; "any new run is a NEW run"]

## Safety / privacy review
- [ ] No secrets or `.env` values exposed
- [ ] No private content logged or persisted
- [ ] No destructive action executed
- [ ] No acceptance threshold weakened
- [ ] Previously passing gates preserved (list them)

## Known limitations
- [honest boundaries of what was built]

## Assumptions
- [decisions made without direct evidence]

## Not tested autonomously (and why)
- [host-bound, human-bound, or budget-bound checks — labeled
  UNEXECUTED_ON_<HOST>, never pass/fail]

## Human validation required
1. [exact steps or a pointer to the queued HVQ item + `PENDING.md` block]

## Merge blockers
- [what still stands between this branch and a merge]

## Recommended next action
- [one concrete, safe, highest-value step]
```

## Rules

- The next worker/reviewer reads, in order: this handoff, the task
  contract, the current `git status`/`git diff`, and the actual test
  outputs — **the repository is authoritative over any prose**, so the
  handoff must match the repo or say where it cannot.
- Never claim an unrun host case as passing or failing. Never round up.
- Reviewers consume the handoff, re-derive the evidence, and record
  findings as dated addenda — they do not edit alongside a worker in the
  same worktree.
- After handoff, update the tracker issue and the durable context
  (dated addenda; manifest re-hashed if files changed).
