# Architecture of the engineering Mission

How the pieces fit: who does what, where state lives, and how the loop
runs over days and weeks.

## Roles

- **Founder** (human) — the decision-maker. Sets direction, authorizes
  R3 and budgets, approves policies, performs (or approves operators
  for) human validation. Interrupted only for real founder decisions.
- **Orchestrator** (`.factory/droids/engineering-manager.md`) — plans the
  Mission, writes task contracts, delegates to workers, routes reviews,
  maintains the queue and durable context, reports truthfully. Does not
  implement features.
- **Specialist workers** — one bounded task each, one writer per surface.
  Workers produce evidence, not claims.
- **Independent reviewer** — an agent or human who did **not author** the
  change, running `.factory/skills/independent-review/SKILL.md`. The
  author never performs the final review of their own high-risk change.
- **Operator** (human, optional) — a qualified non-engineer who executes
  written validation procedures verbatim on a required host
  (`.factory/skills/host-validation/SKILL.md`). If a step is not written
  down, it does not happen.

## Surfaces (one job each)

| Surface | Job |
|---|---|
| GitHub / forge | Code, branches, PRs, review evidence, sanitized results, durable context. |
| Tracker (Linear) | The active execution queue; every task/blocker/gate is an issue with dependency labels (`docs/linear-workflow.md`). |
| Durable context (`docs/agent_handoff/`) | Operating memory; any new agent resumes from it without reading old sessions. |
| `human_tests/` | The host/human evidence boundary: `PENDING.md` requests → `results/<id>.md` sanitized results. |
| `agent_reports/` | Dated daily reports (`YYYY-MM-DD.md`). |
| Skills (`.factory/skills/`) | Repeatable procedures as checklists. |
| Droids (`.factory/droids/`) | Agent specializations (orchestrator, workers, reviewer). |

## The durable context bundle

```
docs/agent_handoff/
  00_README.md            index: as-of anchors, authority, read order, resumability test
  10_durable_instructions/   principles, decision record (dated), rules/red-lines/stops
  20_workflows/           operating loop, escalation, onboarding, handoff maintenance
  30_current_state/       repo/hosts, gates and sign-offs, test commands, architecture notes
  40_historical_evidence/  dated facts, provenance manifests, analysis records
  50_active_tasks/        status of active tasks, completed/blocked lists, EXACT NEXT SAFE ACTION
  60_migration/           notes for moving the model between agent platforms
  HOST_VALIDATION_QUEUE.md
  MANIFEST.md             checksums for tamper detection and transfer integrity
```

## Bootstrapping the bundle (day one)

Create `docs/agent_handoff/` with four files — the fastest path is to
copy `templates/agent_handoff-skeleton/` into it and fill the
placeholders (the skeleton ships all four files below, plus header-only
starters for the remaining tiers) — and the rest of the tiers accrue as
the Mission runs:

- **`00_README.md`** — the index. Must contain: an **as-of anchor**
  (date, `main` HEAD SHA, frozen evidence branch SHA if any, open PRs —
  "verify every SHA/state before use"), the authority/precedence list,
  the read order, and the resumability test checklist.
- **`HOST_VALIDATION_QUEUE.md`** — seeded from the schema in
  `.factory/skills/host-validation/SKILL.md` §5 (empty table, dated
  header block).
- **`MANIFEST.md`** — tamper detection for the bundle: one line per
  bundle file (`sha256sum docs/agent_handoff/<file>` output; stock macOS
  uses `shasum -a 256`, which writes the same line format); re-hash
  any entry whose file changed, in the same commit as the change. A
  file cannot contain its own checksum, so `MANIFEST.md` itself stays
  unlisted.
- **`10_durable_instructions/`** — at minimum the dated decision record
  (founder decisions, newest wins) and the rules/red-lines file. The
  remaining directories ship in the skeleton as header-only starters
  and fill in when first used.

A brand-new agent must be able to resume from the bundle alone. The
resumability test passes when it knows: who the founder is and the
authority channel; the risk tiers and the 7 conditional-merge
conditions; the refs/SHAs and open PRs; the host rules; active tasks
and blockers; and the **exact next safe action**.

## Maintenance (what makes the memory durable)

- **Dated addenda only.** Never rewrite old records to look current;
  newest dated entry wins. Historical text stays as history, explicitly
  marked superseded.
- **Update triggers:** task completed, PR opened/merged/head moved
  materially, new blocker or human gate, new host evidence, founder
  decision, policy/architecture change. Skip: routine commits, wording
  tweaks, transient re-runs with unchanged results.
- Every entry cites `file@SHA` or a PR link, says "verify before use"
  where state may have moved, and contains **no secrets and no raw
  private evidence**.
- **Resumability test** (in `00_README.md`): could a brand-new agent
  start from the bundle alone — knowing the founder, authority, risk
  tiers, refs and PRs, host rules, active tasks, and the exact next safe
  action? Keep that checklist green.

## The operating loop

**Startup (every fresh session):** read durable instructions and current
state; inspect remote, branches, HEAD, dirty work, worktrees, open PRs,
the tracker queue, the host validation queue; verify task artifacts
exist; reconcile records against repository evidence; list red lines,
pending host evidence, and the review backlog. Never restart from
assumptions when the working tree already contains work.

**Per task (15 steps):**

1. select the highest-value unblocked item;
2. classify risk tier and execution environment;
3. write the task contract (`templates/task-contract.md`);
4. capture baseline evidence with provenance;
5. inspect the implementation before editing;
6. make the smallest general change the risk tier allows;
7. add regression coverage;
8. test on the correct host (queue host items, do not fake them);
9. produce durable evidence at an exact SHA;
10. update durable context and docs;
11. commit (staged by name, agent identity);
12. push the agent branch;
13. open/update the PR (R2: draft until review);
14. escalate if a review or human gate is needed;
15. pick the next item — never idle while safe work exists.

**Worker/reviewer separation:** a worker stops at a clean checkpoint,
updates its handoff (`templates/worker-handoff.md`), and the reviewer
works from that handoff and the actual diff — never the two in the same
worktree at once, never the author reviewing their own change. Reviewers
assume the worker may have made subtle mistakes and specifically attack
false-positive verification, weakened bars, and boundary leaks.

## When blocked

Post one escalation — once — then continue safe work:

```text
BLOCKER:
WHAT I TRIED:
EVIDENCE (file@SHA / PR / command output summary):
RISK IF IGNORED:
DECISION NEEDED (bounded options + recommendation):
SAFE WORK CONTINUING MEANWHILE:
```

Blocked paths are re-queued with their unblocking condition
(`needs-machine` / `needs-human` / `needs-founder`, `needs-<host>`); the
Mission keeps moving on everything else.

## Example lifecycle (one task, end to end)

```text
tracker issue (contract + evidence bar)
  → worker implements on agent branch (R1/R2)
  → focused tests + regressions at exact SHA
  → host-specific evidence requested (HVQ item → PENDING.md)
  → operator/founder runs it on the host → sanitized results file
  → independent review (7 conditions) → APPROVE
  → conditional merge (R2) / merge after explicit founder authorization (R3)
  → affected checks re-run before/after, queue + durable context updated
  → issue closed with a pointer to evidence; daily report filed
```
