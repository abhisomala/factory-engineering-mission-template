---
name: human-dependency-audit
description: Audit everything the Mission is waiting on the founder for, classify each wait (needs-machine / needs-human / needs-founder), and produce a bounded delegation-and-automation proposal that reduces founder interruptions without weakening evidence, safety, or review. Use when the queue accumulates founder-blocked items, when a recurring ask is noticed, or as a periodic review.
---

# Human-dependency audit

The failure mode this skill prevents: a capable engineering Mission that
ships work constantly, yet stalls in a long queue of "waiting for the
founder" items — most of which do not actually need the founder. The goal
is that **the founder is interrupted only for real founder decisions**:
R3 actions, exceptional spending, policy, and human experiences where their
participation specifically matters.

Never use this skill to lower a bar, delete a hard case, substitute hosts,
or weaken evidence. Delegation changes *who executes*, never *what counts
as proof*.

## 1. Inventory the waits

Collect every item currently waiting on a human: tracker issues with a
`needs-founder` or `needs-human` label, host-validation queue rows, PRs
awaiting review or a founder decision, budget requests, and recurring
manual asks (setup, test accounts, permission grants, sign-ins). For each,
record: what the manual action is, why it exists, how often it recurs, and
what evidence it produces.

## 2. Classify each wait

- **needs-machine** — no human is required at all; a machine can do it
  safely (a test, a build, a static check, a scripted procedure on an
  available host). If it is still waiting on a human, that is a
  classification bug: automate it or assign it to a worker. (This label is
  a template extension of the source system's host-specific label — e.g.
  its `needs-<host>` — generalized to "no human required at all".)
- **needs-human** — a specific human is required, but **not the
  founder**: any qualified operator following a written procedure
  (running a host validation block, listening to an audible check,
  confirming a physical precondition, sitting at a device).
- **needs-founder** — only the founder can decide or act: R3
  authorization, budgets and credentials, policy and governance changes,
  benchmark/corpus/scoring approval, merge and release decisions, genuine
  human-experience validation (the experience of a real user *is* the
  requirement), and anything with irreversible or privacy consequences.

Push items leftward: needs-founder → needs-human → needs-machine, only
when evidence quality is preserved. Update tracker labels to match
(`docs/linear-workflow.md`).

## 3. For each proposed reduction, write the proposal item

Structure every item the same way (full template:
`templates/founder-dependency-reduction-prompt.md`):

- **Manual action before** — what the founder does today and why it
  existed (usually: trust in the executor, no written procedure, or a
  one-time setup that became recurring).
- **Replacement** — the mechanism: a written operator procedure, a
  bounded standing authorization with expiry, a one-time bootstrap
  checklist, a synthetic test surface, or automation on an available
  host.
- **Evidence quality** — EQUAL, STRONGER, or (rarely, and only with
  explicit justification) a consciously accepted trade. Same commands,
  same exact-SHA rule, same status vocabulary, same independent review.
- **New risks + mitigation** — e.g., operator error → verbatim-only rule
  + stop conditions + unchanged review.
- **Rollback** — how to revoke the delegation instantly.
- **What stays founder-only** — name the things this item must never
  touch.

## 4. The delegation toolkit (in order of preference)

1. **Automate on an available host** (needs-machine). If a machine can
   safely produce the evidence, no human should be in the loop.
2. **Delegate to a qualified operator** (needs-human). Write the operator
   packet under `human_tests/operator/`: a bootstrap checklist (one-time
   setup), a session runbook, the current request block executed
   verbatim, and stop conditions (any permission prompt, any step not
   written down, any unexpected private content, any undeclared
   purchase/send/password request → stop and report). The operator never
   improvises.
3. **Bounded standing authorizations with expiry** (replaces per-run
   asks). Each is a narrow scope, an exact procedure, a stop condition,
   a reporting requirement, an expiry (e.g., 30 days), instant
   revocability, and a ledger for anything metered (predeclared caps,
   used/remaining reported per run). A blanket grant is never the goal;
   a bounded, auditable, revocable envelope is.
4. **One-time setup instead of recurring setup.** Make recurring grants
   and installs a bootstrap checklist performed once, with a read-only
   preflight checker that reports status without ever triggering
   prompts.
5. **Synthetic test surfaces.** Founder-approved disposable surfaces
   (a test account that can only message itself, a scratch calendar, a
   sandbox page) so routine tests never touch real data. Creating each
   surface once is a founder act; routine use is delegated.
6. **Batch irreducibly-human work.** Some steps genuinely need elevated
   privileges or the founder in person. Batch them so they are asked for
   once, not per-task. Do not build privilege-escalation shims to avoid
   the ask.

## 5. What never delegates (guardrails for every proposal)

- R3 actions and real external side effects.
- Budget and credential approval (standing envelopes may pre-authorize
  capped use, never expand it).
- Approval of validation scope, benchmarks, corpora, and scoring.
- Independent review and merge decisions.
- Genuine human-experience validation where the human experience is the
  requirement (an operator can run it; the founder approves and often
  conducts it; a simulation can never replace it).
- Approving the delegation itself, and revoking it.

## 6. Record decisions; keep the audit honest

- Present the proposal to the founder **per item** (approve/reject
  independently, never as a bundle).
- On approval, record it in the durable context decision record (dated
  addendum) and update tracker labels. On rejection, record why.
- Track the outcome: did founder interruptions actually drop, with
  evidence quality held equal? If a delegation produces bad evidence,
  revoke it and revert — that is the audit working, not failing.

## Success criteria

A run of this skill ends with: a classified inventory of waits, a per-item
proposal with evidence-quality and rollback analysis, updated tracker
labels, and a recorded founder decision — with no bar lowered, no
independent review removed, and no human-experience check replaced by a
machine claim.
