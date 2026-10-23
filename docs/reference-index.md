# Reference index

One line per shipped file: what every file in the template is, so a
reader can see the whole system on one screen. The machine-checked
structure is the README contents tree (which this index deliberately
mirrors in scope); the index adds the human answer — what each file is
for. Runtime paths adopters create (`docs/agent_handoff/`,
`human_tests/`, and their own dated `agent_reports/` entries) are not
listed here because they are not shipped in the template; this
repository's own development record under `agent_reports/` is shipped
and is listed.

As of: 2026-10-23 — 41 shipped files (verify with `git ls-files`).
Update this file in the same change that adds or removes a shipped
file; every path below must resolve (the validator's reference check
enforces that mechanically).

| File | What it is |
|---|---|
| `AGENTS.md` | Compact, always-on governance every session loads first: precedence, risk tiers, red lines, conventions. |
| `README.md` | The front door: the problem, fit and non-fit, the five-step quickstart, contents tree, verifying your copy, customizing. |
| `LICENSE` | MIT license, copyright the template's contributors. |
| `.gitignore` | Keeps secrets, env files, logs, and local artifacts out; raw host artifacts stay on the host where they were produced. |
| `.factory/droids/engineering-manager.md` | The orchestrator (Engineering Manager) droid: operating model, seven-step loop, truthful reporting, hard boundaries. |
| `.factory/skills/independent-review/SKILL.md` | The R2 conditional-merge gate: seven conditions with verification steps, three verdicts, required output format. |
| `.factory/skills/host-validation/SKILL.md` | The host-evidence workflow: queue rules, request format, result recording, host status vocabulary. |
| `.factory/skills/human-dependency-audit/SKILL.md` | Classifies every human wait and drafts per-item delegation proposals without lowering any bar. |
| `templates/mission-start-prompt.md` | Paste-ready prompt (replace bracketed placeholders) that starts a Mission: objective, reconciliation, per-task loop, boundaries, reporting. |
| `templates/mission-approval-prompt.md` | One-screen founder decision request: bounded options, a recommendation, and exactly what happens after approval. |
| `templates/founder-dependency-reduction-prompt.md` | The audit's output format: inventory of waits, per-item reduction proposals, and the guardrails section. |
| `templates/task-contract.md` | The contract written before any substantial task; the review anchor that acceptance evidence is judged against. |
| `templates/worker-handoff.md` | The checkpoint handoff a worker writes before stopping, for a reviewer or successor who was not present. |
| `templates/readiness-checklist.md` | Adoption readiness: what the adopted-mode machine check proves, and the external human gates it cannot. |
| `templates/agent_handoff-skeleton/00_README.md` | Day-one starter for the bundle index: as-of anchor, precedence, read order, resumability test. |
| `templates/agent_handoff-skeleton/HOST_VALIDATION_QUEUE.md` | Day-one starter for the host validation queue: dated status block plus the row schema. |
| `templates/agent_handoff-skeleton/MANIFEST.md` | Day-one starter for bundle integrity hashes: one sha256 line per bundle file. |
| `templates/agent_handoff-skeleton/10_durable_instructions/decision-record.md` | Starter for the dated decision record (newest first, addenda only, superseded entries stay). |
| `templates/agent_handoff-skeleton/10_durable_instructions/rules-and-red-lines.md` | Starter for project-specific rules, red lines, and stop conditions that accrue as addenda. |
| `templates/agent_handoff-skeleton/20_workflows/README.md` | Header-only starter where the operating loop, escalation, and onboarding notes accrue. |
| `templates/agent_handoff-skeleton/30_current_state/README.md` | Header-only starter for current repo/host state, gates and sign-offs, test commands. |
| `templates/agent_handoff-skeleton/40_historical_evidence/README.md` | Header-only starter for dated facts, provenance manifests, and analysis records. |
| `templates/agent_handoff-skeleton/50_active_tasks/README.md` | Header-only starter for active-task status and the exact next safe action. |
| `templates/agent_handoff-skeleton/60_migration/README.md` | Header-only starter for notes on moving the operating model between agent platforms. |
| `docs/risk-model.md` | The R0–R3 tiers, the seven conditional-merge conditions, standing authorizations, and repository safety rails. |
| `docs/evidence-policy.md` | What counts as proof: proven/unproven/blocked, attempt vs action vs verified result, status vocabularies, sanitization, benchmark integrity. |
| `docs/linear-workflow.md` | Tracker conventions: one issue per bounded task, dependency and risk labels, queue ordering, secondary-repository writes. |
| `docs/architecture.md` | Roles and surfaces, the durable-context bundle and its maintenance rules, the fifteen-step operating loop, the escalation format. |
| `docs/maturity.md` | The template's honest proven-vs-unproven self-assessment, kept current as gaps close. |
| `docs/mission-plan.md` | This template's own development mission: milestones with a status column, founder gates, resumption rules. |
| `docs/worked-example-schema.md` | What the validator's worked-example checks require, and the synthetic-evidence limits a PASS does not cross. |
| `docs/reference-index.md` | This file: one line per shipped file, kept in scope with the README contents tree. |
| `examples/example-linear-queue.md` | Illustrative tracker queue with labels, states, and a validation request flowing through it. |
| `examples/example-daily-report.md` | The daily-report format shown filled in (a synthetic day). |
| `examples/worked-example.md` | Synthetic end-to-end R1 and R2 lifecycles: tracker issue, contract, handoff, review, merge, post-merge records. |
| `examples/worked-r3-example.md` | Synthetic R3 authorization done right: escalation, dated decisions, standing ledger, attempt/action/verified-result execution. |
| `examples/worked-host-validation.md` | Synthetic host-validation item end to end: queue rows, request block, operator note, sanitized result. |
| `scripts/validate.py` | Structural self-validation: contents tree, internal references, worked-example schemas, plus the separate adopted-repo mode. |
| `scripts/worked_examples.py` | The narrow, structure-only schemas behind the third validator check; reads the three examples and nothing else. |
| `scripts/test_validate.py` | Twenty-six offline validator regressions in disposable copies: positives, mutated fields, broken gates, adopted modes. |
| `agent_reports/2026-10-22.md` | Day 1 and Day 2 development record: cold-start test, snag table, exact validation runs. |
