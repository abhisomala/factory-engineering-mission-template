# The R0–R3 risk model

Autonomy is not all-or-nothing. The Mission classifies every task by the
damage its failure could cause, and grants the agent exactly the freedom
that risk level supports — no more, no repeated approvals where a
standing rule suffices, and no self-approval where independence or a human
is required.

## The tiers

| Tier | Definition | Autonomy |
|---|---|---|
| **R0** | Docs, research, fixture creation, analysis, benchmark source review. No production behavior changes. | Fully autonomous. |
| **R1** | Bounded implementation or refactor of ordinary behavior. | Autonomous, with focused tests. Commit and push agent branches; open PRs. |
| **R2** | Anything that changes what "correct" means or guards it: verification and acceptance logic, safety and confirmation flows, privacy and data flow, credentials, telemetry, permissions, and **any change to a test, gate, benchmark, or acceptance bar attached to such surfaces**. | Implement, test, commit, push, and open PRs **without prior approval**. Merge only when every independent-review condition holds (below). |
| **R3** | Real external side effects: sends, deletes, purchases, account changes, releases, visibility changes, privacy expansion — anywhere they can occur, including from inside tests. | **Explicit human authorization before execution, every time.** Some actions may additionally be human-only by policy. |

Two rules keep the tiers honest:

- **When in doubt, classify up.** A task that mostly looks R1 but touches
  verification logic is R2.
- **The classification is per-consequence, not per-file.** Editing a
  config file can be R3 if the config enables a real external effect.

## Conditional R2 merge (the 7 conditions)

An R2 change may be merged without a per-merge human approval when **all**
of the following hold, verified by the independent-review skill:

1. The required evidence exists (assertions without artifacts are not
   evidence).
2. Required host evidence actually came from the required host, at the
   exact head SHA being merged.
3. No previously passing gate regresses.
4. Tests and benchmarks were not weakened (including: any changed
   assertion is justified in writing and re-checked against a known-failing
   case).
5. Safety and privacy boundaries are preserved.
6. The final review is independent of the authoring worker.
7. The PR accurately states what is and is not proven, with host labels.

If any condition fails, the PR stays `WAITING_FOR_REVIEW`, the missing
piece is queued, and the Mission continues other work. Full checklist:
`.factory/skills/independent-review/SKILL.md`.

**R3 is never satisfied by review.** Review can catch an unapproved R3
action and stop it; it can never authorize one.

## Standing authorizations instead of repeated approvals

Repeated per-run approvals waste the human's attention. Where a class of
action recurs, replace per-run asks with a **bounded standing
authorization**:

- narrow scope (exact procedure, exact surfaces),
- a stop condition (any deviation, any prompt, any unexpected content),
- a reporting requirement (one result file per use, metered ledger
  reported per run),
- an expiry (e.g., 30 days), instant revocability, and renewal in one
  word.

Prefer these for: non-destructive validation runs by an authorized
operator, mutations of declared disposable test surfaces, self-addressed
test sends, and predeclared metered budgets with hard caps. Never use
them to expand R3 authority — a standing envelope can cap and pre-spend a
budget, never enlarge one. Audit them with
`.factory/skills/human-dependency-audit/SKILL.md`.

## Review backpressure

Human review is the scarcest resource in the loop. Cap it:

- At most **~2 substantial unreviewed PRs** open at once (or ~30–45
  minutes of estimated review backlog).
- At the cap, mark work `WAITING_FOR_REVIEW` and switch to R0 work
  (research, docs, fixtures, non-conflicting surfaces) until reviews catch
  up.
- One writer per production surface; parallel workers only on
  non-conflicting surfaces or isolated worktrees.

## Repository safety rails

- `main` is protected by a ruleset that rejects agent direct pushes.
- Agent branches: `agent/YYYY-MM-DD/<task-slug>`. Never force-push; never
  rewrite published history.
- Keep a frozen provenance branch for evidence snapshots; never merge,
  modify, or delete it. **What it is for:** an immutable historical
  baseline you can compare against (A/B runs, characterization tests,
  before/after evidence) while verification or acceptance logic is being
  rewritten. **When to create one:** right before a risky rewrite of any
  evidence-bearing surface (verification logic, benchmarks, gates) —
  branch or tag the current known-good tree, then never touch it. If you
  have nothing worth freezing yet, the rule is dormant, not optional:
  the first risky rewrite is when it becomes load-bearing.
- Scoped credentials: agents write through a dedicated scoped credential
  (e.g., delivered via Factory Secrets) used via a credential helper
  with a clean remote URL — never a token-embedded remote, and never
  printed, logged, echoed, or persisted. Broader personal credentials on
  the host stay read-only for agent work. Credential-path deviations are
  recorded as incidents, never silently repeated.
- Commits carry a distinct, non-secret agent identity (never the founder's
  personal identity) so authorship is auditable.
- Metered runs (paid APIs, budgeted compute) require an explicit recorded
  budget with a hard cap before starting; no repeats or expansion without
  asking. A budget that was authorized and unspent is recorded as such
  (`UNSPENT / DEFERRED`), so it is never silently re-used for a different
  purpose.

## Worked examples

- "Refactor the payment module's internal helpers, add unit tests" — R1
  (no verification-logic or external-effect change).
- "Change the acceptance check that decides whether a UI action is
  reported CONFIRMED" — R2: independent review required, and the changed
  assertion must be justified against a known-false-confirm case.
- "Add a nightly job that files a real issue in the production tracker
  on failure" — R3 the first time it runs against production (external
  side effect); R0/R1 while built against a sandbox tracker.
- "Run the benchmark suite once more to confirm yesterday's number" —
  metered: needs a budget, and the new run is a **new** run, never a
  confirmation of the old one.
