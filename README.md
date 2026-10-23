# Factory Engineering Mission Template

A reusable operating system for long-running, multi-agent engineering with
Factory: an orchestrator that delegates to specialist workers, risk-tiered
autonomy, evidence-based completion, independent review of high-risk
changes, host-specific validation, and a structured path for spending the
founder's attention only where it is actually required.

**Adoption time, measured once (2026-10-22): a zero-context machine-paced
reader completed reading plus the local copy-and-seed steps in about
seven minutes (7m03s at machine speed). The platform setup in step 3 —
branch protection, credential, tracker labels, Mission start — is
external, extra, and varies. Human-paced timing is unmeasured.**

---

## The problem this template solves

AI agents can generate unlimited work. What they cannot do by default is:

- tell the truth about what is actually **proven** versus merely attempted;
- stop themselves from **weakening tests** to make a gate go green;
- resist claiming **host-specific results** (a real device, OS, or
  environment) from whatever machine they happen to run on;
- avoid turning every small decision into a **queue of founder
  interruptions** — while also not silently grabbing authority they were
  never given.

This template installs the missing operating model. It was extracted from
a real, long-running autonomous engineering project and generalized: its
rules come from observed failure modes — false success claims, weakened
acceptance bars, wrong-host evidence, idle missions blocked on a human,
and unsupervised merges of the very logic that decides what "done" means.
A small number of mechanisms are extensions of the source system rather
than direct extractions; they are flagged in place.

The core promise: **the agents ship; the founder decides.** Work moves at
machine speed on everything below the risk line, and the founder's
attention is reserved for the decisions that are genuinely theirs.

## Is this for you?

**It fits** long-lived engineering repositories where autonomous agents
do real work and the founder is the bottleneck: delegated autonomy with
audit trails is the point, and a forge plus a tracker are already in
place (or cheap to add).

**It requires** an agent platform that loads `.factory/droids/` and
`.factory/skills/` (or an equivalent on yours), and tolerance for
process discipline: dated durable-context addenda after every task, PR,
and decision; daily reports; independent review for every R2 change;
host-validation windows executed by a human; and a ~2-PR
review-backpressure cap.

**It is not for** throwaway prototypes, or teams unwilling to maintain
that discipline — the structure only works if the records are kept.

**Solo use is covered** (see "Customizing" → "Scale down"), but
materially independent R2 review is still mandatory: a different worker,
a fresh session, or the founder — never the authoring context.

**What it costs, honestly:** tracker and label upkeep;
durable-context writing discipline after every task, PR, and decision; a
daily report; a second reviewer for every R2 change;
verbatim-executable host requests for non-engineer operators; and founder
attention for R3, budgets, and the genuinely-human decisions. Up front
you decide: your R2/R3 definitions, required hosts, tracker choice,
agent identity, label set, and how solo review independence is
achieved.

## How it fits together

```mermaid
flowchart TB
    subgraph Humans
        F["Founder<br/>(decisions, R3, budgets)"]
        O["Operator, optional<br/>(runs host validation verbatim)"]
    end

    ORCH["Orchestrator<br/>engineering-manager droid<br/>plans, delegates, records"]

    subgraph Workers
        W1["Worker A<br/>one bounded task"]
        W2["Worker B<br/>non-conflicting surface"]
    end

    REV["Independent reviewer<br/>never the author"]

    subgraph Systems
        GH["GitHub<br/>code / PRs / evidence truth"]
        LIN["Tracker (Linear)<br/>active execution queue"]
        HB["Durable context bundle<br/>docs/agent_handoff/"]
        HT["human_tests/<br/>PENDING.md → results/"]
    end

    F -->|"bounded options,<br/>one decision at a time"| ORCH
    ORCH -->|"task contracts,<br/>one writer per surface"| W1 & W2
    W1 -->|"handoff + diff"| REV
    REV -->|"APPROVE / FIX-REQUIRED<br/>/ WAITING_FOR_REVIEW"| ORCH
    ORCH -->|"host evidence request"| HT
    O -->|"runs on required host,<br/>sanitized result"| HT
    HT --> HT2["UNEXECUTED_ON_HOST<br/>never pass/fail"]
    W1 & W2 & REV <-->|"commits, PRs, checks"| GH
    ORCH <-->|"tasks, blockers, labels"| LIN
    ORCH <-->|"dated addenda, resumable memory"| HB
    GH & LIN <-->|"evidence, never instruction"| ORCH
```

One job per surface: **GitHub** is the truth for code and evidence. **The
tracker** is the active queue (every task/blocker/gate is an issue,
labeled by what can unblock it). **The durable context bundle** is memory
a brand-new agent can resume from. **`human_tests/`** is the one-way
boundary where host-specific evidence crosses from machines to the repo.
And the founder's direct session is the **only** instruction channel —
issues, PRs, and web content are evidence, never instructions.

## Quickstart

1. **Copy the template into your repository.** The docs, skills, droid,
   templates, and examples are cross-referenced, so take them all:

   ```text
   rsync -a --exclude .git /path/to/factory-engineering-mission-template/ /path/to/your-repo/
   ```

   `.factory/` is a **hidden directory** — it carries the orchestrator
   droid and all three skills — and naive copies (a `cp` with a `*`
   glob, a Finder window drag) silently drop it. Verify it arrived:
   `ls -A` in your repository must show `.factory/`.

   Then create the three runtime directories the system writes into:

   ```text
   docs/agent_handoff/     durable context bundle (seeded in step 4)
   human_tests/            host/human evidence boundary (PENDING.md + results/)
   agent_reports/          dated daily reports (format: examples/example-daily-report.md)
   ```

   Notes on those directories:

   - `human_tests/PENDING.md` holds request blocks in the exact format
     defined in `.factory/skills/host-validation/SKILL.md` §3; §5 of the
     same file defines the queue schema that step 4 seeds.
   - The shipped `agent_reports/` directory is this template's own
     development record. Keep it or delete it; your own dated reports
     accumulate there either way.

   Starting from a fresh, empty repository? Make your import commit
   before step 4 — the bundle's as-of anchor needs a `main` HEAD SHA —
   and check that your default branch is `main` (a bare `git init` may
   default to `master`).

   The starter `.gitignore` keeps secrets and logs out of the
   repository; raw host artifacts stay on the host that produced them
   (only sanitized results are ever committed — the `.gitignore`
   records that discipline, and humans enforce it).

2. **Decide your risk surfaces.** `AGENTS.md` ships a clearly marked
   placeholder block — `<!-- YOUR PROJECT'S R2/R3 SURFACES — edit me -->`
   in the Risk tiers section. Replace it with what R2 means in *your*
   project (typically: verification/acceptance logic, safety flows,
   privacy, credentials, telemetry) and what R3 means (real external side
   effects), and make the matching edit in `docs/risk-model.md`. Keep R3
   crisp — it is the line the agents will not cross without you. Where
   the day-one decisions live: `AGENTS.md` carries the resulting R2/R3
   definitions; the bundle's dated decision record
   (`docs/agent_handoff/10_durable_instructions/decision-record.md`,
   seeded in step 4) holds the decision itself.

3. **Protect `main` and scope the agents' credential.** Everything in
   this step is **EXTERNAL** — it happens on your forge and your
   credential store, not in this repository, and no repo-local check can
   verify any of it.

   - **Branch protection (EXTERNAL).** Add a ruleset that rejects every
     non-PR push to `main`: all changes arrive by pull request, for every
     credential, including the agents'. On GitHub that is a branch
     ruleset targeting `main` with "Require a pull request before
     merging" and no bypass entries for agent identities.
   - **Scoped agent credential (EXTERNAL).** Give the agents their own
     fine-grained token — never your personal one. Example scope for a
     GitHub fine-grained PAT limited to this one repository: Contents
     **Read & write**, Pull requests **Read & write**, Issues
     **Read & write**, Metadata **Read** (mandatory) — and nothing else:
     nothing administrative, no organization-level permissions.
   - **Clean remote + credential helper (EXTERNAL).** The remote URL
     never contains a token; a helper supplies the credential at call
     time:

     ```text
     git remote set-url origin https://github.com/<org>/<repo>.git
     git config credential.helper \
       '!f() { printf "username=%s\npassword=%s\n" "agent-bot" "$(cat "$AGENT_TOKEN_FILE")"; }; f'
     ```

     The token comes from a secret store (e.g., Factory Secrets or your
     platform's equivalent) exposed to agent sessions as a file or
     environment variable; it is never printed, logged, echoed, or
     persisted in the repository. Broader personal credentials on the
     host stay read-only for agent work. Any credential-path deviation
     (token printed, token embedded in a URL, wrong credential used) is
     recorded as a dated incident in
     `docs/agent_handoff/30_current_state/` — never silently repeated.
   - **Agent commit identity (the only repo-local part).** Example
     values — distinct, non-secret, never the founder's:

     ```text
     git config user.name  "Engineering Bot"
     git config user.email "123456789+engineering-bot@users.noreply.github.com"
     ```

4. **Create the queues.** Two queues: the tracker and the durable
   context bundle.

   - **Tracker labels (EXTERNAL).** Create the label set from the
     canonical definitions in `docs/linear-workflow.md` § Labels:
     `needs-machine` / `needs-human` / `needs-founder` (who or what can
     unblock an issue), `R0`–`R3` (risk tier), and optionally
     `needs-<host>` (e.g., `needs-macos`) and `metered` (budgeted runs).
     `examples/example-linear-queue.md` shows the labels in use;
     `docs/linear-workflow.md` is the definition.
   - **Durable context bundle (local).** Copy
     `templates/agent_handoff-skeleton/` into `docs/agent_handoff/`
     and fill the placeholders. That seeds all four day-one files the
     bootstrap guide (`docs/architecture.md` § "Bootstrapping the bundle
     (day one)") requires — `00_README.md` (index: as-of anchor,
     precedence, read order, resumability checklist),
     `HOST_VALIDATION_QUEUE.md` (schema:
     `.factory/skills/host-validation/SKILL.md` §5), `MANIFEST.md`
     (integrity hashes; stock macOS uses `shasum -a 256`), and
     `10_durable_instructions/` (dated decision record + rules/red
     lines) — plus header-only starters for the remaining tiers.

5. **Start the Mission.** Paste `templates/mission-start-prompt.md` with
   your objective into a Factory Mission (or any session running the
   engineering-manager droid). In Factory, files under `.factory/droids/`
   are loaded automatically for sessions in that repository — the droid
   file is the orchestrator's role definition — and `.factory/skills/`
   likewise appears as available skills; on another platform you need an
   equivalent way to load the droid and skills into the session. The
   Mission will reconcile state, propose the first three tasks with risk
   tiers and evidence bars, and begin.

From then on, the three skills run the loop: reviews use
`independent-review`, host evidence uses `host-validation`, and whenever
the queue fills with founder-blocked items, run the
`human-dependency-audit`.

## Mission orchestration

The orchestrator (`.factory/droids/engineering-manager.md`) does not
implement. It runs a loop:

1. **Reconcile** — inspect repo, PRs, queues, and durable context;
   records must match repository evidence before planning.
2. **Plan** — pick the highest-value unblocked item; classify its risk
   tier and required execution environment; write the task contract
   (`templates/task-contract.md`) with the acceptance evidence bar.
3. **Delegate** — one bounded task per worker, one writer per surface.
4. **Verify** — a task is complete only when its evidence exists at an
   exact SHA. Never "code written".
5. **Route** — high-risk changes to an independent reviewer; host-bound
   evidence to the validation queue; R3 and budgets to the founder with
   bounded options.
6. **Record** — tracker, durable context (dated addenda), daily report.
7. **Continue** — never idle while safe work exists; blocked lanes get
   one escalation and a re-queue.

Every substantive report to the founder follows the same contract:
**Changed / Evidence / Risk / Proven-vs-unproven / Next action.**

## Worker/reviewer separation (example)

> A worker implements a change to the code that decides whether an action
> is reported `CONFIRMED` (an R2 surface: verification logic). Its
> fixture tests pass, so it opens a draft PR, writes its handoff
> (`templates/worker-handoff.md`), and **stops editing**. A different
> worker picks up the independent-review skill and re-derives everything:
> Does the required evidence exist? Did host evidence really come from the
> host? Did any passing gate regress? **Was any assertion weakened?** Are
> safety/privacy boundaries intact? Is this review independent? Does the
> PR say precisely what is unproven? All seven hold → `APPROVE` and a
> conditional merge. Any fails → `FIX-REQUIRED` or `WAITING_FOR_REVIEW`
> with the exact missing piece queued.

The separation is the point: the author of a change is the least
trustworthy reviewer of it, and the most dangerous failure — quietly
weakening what "done" means — is invisible unless someone else
re-derives the evidence.

## The tracker (Linear) workflow

Every task, blocker, human gate, and decision is a tracker issue, labeled
so the queue sorts by **what can unblock it**:

- `needs-machine` — no human required; if it idles, automate it.
- `needs-human` — a qualified human (not the founder) runs a written
  procedure.
- `needs-founder` — R3, budgets, policy, merge/release, genuine
  human-experience validation. Keep this list short.

Plus risk labels (`R0`–`R3`) and optional `needs-<host>` / `metered`.
Issues carry their acceptance evidence bar; comments follow the
`[AGENT]` reporting contract; after each merge, affected checks re-run at
exact before/after SHAs. A full worked example, including a host
validation request flowing through `INCOMPLETE`, is in
`examples/example-linear-queue.md`.

## R0–R3: the risk model

| Tier | What | Autonomy |
|---|---|---|
| R0 | Docs, research, fixtures, analysis | Full |
| R1 | Bounded implementation/refactor | Full, with tests |
| R2 | Verification/safety/privacy/credentials/telemetry + **any test or bar attached to them** | Implement and PR freely; merge only when 7 independent-review conditions hold |
| R3 | Real external side effects | **Founder authorization, every time** |

The full model — including the 7 conditional-merge conditions, standing
authorizations with expiry, review backpressure (~2 unreviewed PRs),
budget discipline, and worked examples — is in `docs/risk-model.md`.

## Evidence and verification

`docs/evidence-policy.md` is the template's spine:

- **Proven / unproven / blocked** are always separated; proven means an
  artifact exists at a stated SHA.
- **Attempt ≠ action ≠ verified result.** A successful API call or button
  press proves the attempt, not the goal. Truthful `UNCONFIRMED` beats
  false `CONFIRMED`; false confirmation is a red line.
- **Host honesty.** CI on one OS never certifies another; fixtures never
  certify devices; unrun host cases are `UNEXECUTED_ON_<HOST>`, never
  pass/fail. Host evidence crosses exactly one boundary:
  `human_tests/PENDING.md` → operator/founder runs it on the host →
  sanitized `human_tests/results/`.
- **Never weaken a bar to pass.** No deleted hard cases, no post-hoc
  rewritten expectations, no threshold-lowering, no sleeps replacing
  checks. Changed assertions on high-risk surfaces get independent review
  and must be justified against a known-failing case.
- **Benchmark integrity.** Development / regression / sealed-holdout
  sets; every report carries numerator/denominator + commit + env; any
  new run is a new run.

## Human-dependency audit

Periodically (or when the queue fills with `needs-founder`), run the
`human-dependency-audit` skill with
`templates/founder-dependency-reduction-prompt.md`. It inventories every
wait, classifies it, and produces per-item proposals that push work
leftward — needs-founder → needs-human → needs-machine — through:
written operator procedures, bounded standing authorizations (with
expiry, stop conditions, and ledgers), one-time bootstrap checklists,
synthetic test surfaces, and automation. Two invariants survive every
proposal: **evidence quality stays equal or stronger**, and **the
experience of a real human stays human** — a simulation can never
substitute for it. The founder approves items independently; every grant
is recorded, expirable, and revocable in one word.

## Customizing

- **Risk surfaces**: edit `AGENTS.md` + `docs/risk-model.md` to name your
  R2/R3. The labels are stable; the definitions must be yours.
- **Hosts**: the host-validation skill is host-agnostic by design — name
  your required hosts (an OS, a device lab, a browser engine, a
  production environment) and your queue prefix.
- **Tracker**: label names matter more than the tool; the workflow works
  with any tracker that supports labels and states.
- **Droids/skills**: add specialist worker droids per surface
  (implementation, review, research), each keeping the same reporting
  contract. Add skills for recurring procedures; keep each one a
  checklist with concrete verification steps, not prose.
- **Scale down**: solo project? The orchestrator and one worker can be
  the same session — but final review of an R2 change must be materially
  independent of the authoring context: a different worker, a fresh
  session, or the founder. Same-context self-review is never sufficient.
- The template adapts to your operating model, never the reverse: if a
  rule contradicts how you want to work, change the rule and record why
  in the durable decision record.

## Example lifecycle

```text
tracker issue (task contract + evidence bar)
  → worker implements on agent/YYYY-MM-DD/<slug>
  → focused tests + regressions at exact SHA
  → host-bound evidence queued (HVQ row → human_tests/PENDING.md)
  → operator/founder runs on the host → sanitized results file
  → independent review: 7 conditions → APPROVE
  → conditional merge (R2) / merge after explicit founder authorization (R3)
  → before/after checks re-run; queue + durable context + daily report updated
  → issue closed with evidence pointers
```

## Repository contents

```text
AGENTS.md                          compact, always-on governance
LICENSE                            MIT
.gitignore                         keeps secrets and logs out; raw artifacts stay on the host
.factory/droids/engineering-manager.md    mission orchestrator
.factory/skills/independent-review/SKILL.md
.factory/skills/host-validation/SKILL.md
.factory/skills/human-dependency-audit/SKILL.md
templates/mission-start-prompt.md
templates/mission-approval-prompt.md
templates/founder-dependency-reduction-prompt.md
templates/task-contract.md
templates/worker-handoff.md
templates/readiness-checklist.md     adopted-repo readiness (machine + human checks)
templates/agent_handoff-skeleton/00_README.md   day-one bundle starter
templates/agent_handoff-skeleton/HOST_VALIDATION_QUEUE.md
templates/agent_handoff-skeleton/MANIFEST.md
templates/agent_handoff-skeleton/10_durable_instructions/decision-record.md
templates/agent_handoff-skeleton/10_durable_instructions/rules-and-red-lines.md
templates/agent_handoff-skeleton/20_workflows/README.md
templates/agent_handoff-skeleton/30_current_state/README.md
templates/agent_handoff-skeleton/40_historical_evidence/README.md
templates/agent_handoff-skeleton/50_active_tasks/README.md
templates/agent_handoff-skeleton/60_migration/README.md
docs/risk-model.md
docs/evidence-policy.md
docs/linear-workflow.md
docs/architecture.md
docs/maturity.md                    honest proven-vs-unproven self-assessment
docs/mission-plan.md                v0.1 development mission plan and status
docs/worked-example-schema.md       structural checks and synthetic-evidence limits
docs/reference-index.md             one line per shipped file (what each file is)
examples/example-linear-queue.md
examples/example-daily-report.md
examples/worked-example.md
examples/worked-r3-example.md
examples/worked-host-validation.md
scripts/validate.py                structural self-check (stdlib only)
scripts/worked_examples.py         schemas for the three synthetic worked examples
scripts/test_validate.py           isolated offline validator regressions (stdlib only)
agent_reports/2026-10-22.md        Day 1 + Day 2 daily reports (the template's own development record)
```

## Verifying your copy

Run the structural self-check from the repository root:

```text
python3 scripts/validate.py
```

It exits 0 when the README contents tree matches the working tree, every
checked internal file reference resolves, and the three synthetic worked
examples have their required structured artifacts. Otherwise it exits
non-zero and names the failures. These are **structure-only** checks:
filled fields do not prove outcomes, valid authorization, or live-host
evidence. The exact scope and limitations are in
`docs/worked-example-schema.md`. It uses only the Python standard library
and never touches the network. What is proven versus still unproven about
this template is recorded in `docs/maturity.md`.

Run the isolated positive and negative validator regressions with:

```text
python3 scripts/test_validate.py
```

If you have **adopted** the template (quickstart steps 1–4 complete),
also run the adopted-repo check:

```text
python3 scripts/validate.py --adopted
```

It verifies your bootstrap outputs: the runtime directories, the four
day-one bundle files, `human_tests/PENDING.md`, the host-validation
queue's shape, the manifest hashes, and the `AGENTS.md` risk-surface
edit. What it proves — and the external gates only a human can verify —
is paired in `templates/readiness-checklist.md`.

## Limitations and safety disclaimer

- **A template is not oversight.** This structure makes honest behavior
  the easy path; it cannot *force* it. The human who reads the reports
  and runs the validations is a load-bearing component.
- **LLM behavior is probabilistic.** Rules, checklists, and independent
  review reduce the failure rate of agent claims; they do not eliminate
  it. Treat `PROVEN` as "best-evidence-so-far", keep rollback points,
  and protect `main` mechanically rather than trusting convention.
- **Credentials and side effects are yours.** Scoped credentials, branch
  protection, production access, and the definition of R3 must be
  configured by a human, per repository. Never grant agents
  administrative permissions because a template assumed they existed.
- **The audit can be wrong.** A delegation that looks evidence-equal can
  still fail in practice; that is why every grant is revocable and every
  reduction is tracked. Revoke on the first degraded result.
- **No warranty.** MIT license. This template reflects one working
  system, not a guarantee for yours. Adapt it, measure it, and keep the
  parts that earn their keep.
