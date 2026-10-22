# Worked example: an R3 authorization done right

R3 is the line the agents do not cross on their own: real external side
effects — sends, deletes, purchases, account changes, releases, visibility
changes — anywhere they can occur, including from inside tests. R3 needs
**explicit founder authorization before execution, every time**. Review can
catch an unapproved R3 action and stop it; it can never authorize one
(`docs/risk-model.md`).

This example traces one R3 done correctly, in the same synthetic project as
`examples/worked-example.md` — a web dashboard everyone calls **the
console**. Every ID, SHA, date, count, and output below is synthetic and
self-consistent; nothing here happened.

## The situation

The console emails customers a weekly billing digest. This week's digest
went out with the lifetime total printed in the period-total column. The
sanitized incident note records 212 customers affected — no names or
addresses in the repository, ever. Two tasks fall out, and they classify
differently even though they touch the same feature:

- **ENG-110 (R1)** — fix the total computation and add the wrong-column
  regression case. Bounded, no external effect. Built and merged as PR
  #24 at main 91b2e7f; fixtures 9/9 at head 5c9f2e1, proven at fixture
  level on the dev host.
- **ENG-105 (R3)** — re-send the corrected digest to the affected
  segment. A real send through the production mail provider to 212 real
  recipients.

The classification is per consequence, not per file: the fix was R1 even
though the bug had customer-visible impact; the re-send is R3 even though
executing it is one command.

## What the agents did before asking (and what they would not do)

Everything up to the R3 wall was ordinary, provable work:

- ENG-110 merged (PR #24 at 91b2e7f; wrong-column regression case 9/9 at
  head 5c9f2e1; output pasted in the handoff).
- The digest template's rendering was verified against the synthetic
  renderer: 120/120 fixture rows match expected totals.
- The recipient segment was re-derived from the sanitized incident note:
  212 customers.

What they did **not** do: send anything, to anyone, through the real
provider — not the real list, not a "tiny" test message, not a
"quick dry-run against production". The only unverified step was
real-provider delivery, and verifying it requires an actual send — the one
action that is not theirs to take. ENG-105 went to state `Blocked`, labels
`R3, needs-founder, metered`.

## The escalation (posted once, exactly the template's block)

One comment on ENG-105, prefixed `[AGENT]` per `docs/linear-workflow.md`.
The founder decides from one screen; there is no second ask and no
progress spam:

```text
[AGENT] BLOCKER: ENG-105 — re-sending the corrected weekly billing digest
to the 212-customer segment is R3 (a real send to real recipients). Every
preparatory step is done and verified; I will not execute the send without
explicit founder authorization, and review cannot substitute for it.
WHAT I TRIED: fixed the digest total computation and added the wrong-column
regression case (PR #24, merged at 91b2e7f; fixtures 9/9 at head 5c9f2e1);
verified template rendering against the synthetic renderer (120/120 fixture
rows). The only unverified step is real-provider delivery, which requires an
actual send — the one action that is not mine to take.
EVIDENCE (file@SHA / PR / command output summary): PR #24 @ 91b2e7f
(template fix + regression test, merged); fixture output 9/9 at 5c9f2e1
pasted in the worker handoff; sanitized incident note (wrong totals, 212
customers affected — names and addresses stay out of the repo); provider is
the production mail account, cost ≈ 1 currency unit per 500 sends — small
but real, so the run is metered.
RISK IF IGNORED: 212 customers hold digests with wrong totals and may act
on them; the error repeats in next week's digest if the re-send never
happens; every day of delay extends the window.
DECISION NEEDED (bounded options + recommendation):
  (A, recommended) Authorize one capped re-send: 1 self-addressed test send
      to the declared test inbox (verifies real delivery end to end) plus
      the single real re-send to the 212-customer segment; hard cap 220
      messages total; abort on the first provider error; one sanitized
      result file per step; authorization expires 2026-06-12 if unexecuted.
  (B) Authorize the real re-send only, skip the test send (delivery is then
      fixture-only until the provider report returns).
  (C) Defer the re-send; I draft a support note instead (no send happens;
      customers keep the wrong digest).
SAFE WORK CONTINUING MEANWHILE: ENG-106 (R0) — re-send runbook and
support-reply template (PR #25); HVQ-08 request block added to
human_tests/PENDING.md for the next macOS window.
```

## What the Mission did while waiting

Blocked paths never idle the Mission. Between the escalation (09:41) and
the founder's decision (16:05, same day), the workers completed:

- **ENG-106 (R0)** — the re-send runbook and the support-reply template:
  PR #25 opened at 11:20, checks green. R0 work was deliberately chosen so
  nothing waited on the blocked lane.
- **HVQ-08** — the VoiceOver request block was added to
  `human_tests/PENDING.md` for the next macOS window (companion example:
  `examples/worked-host-validation.md`).
- The wrong-column regression case from ENG-110 was double-checked against
  the sealed holdout discipline: the holdout was not touched; the case
  entered the regression set, never the tuning set.

One escalation, one screen of options, zero idling.

## The founder's decision (dated decision-record entries)

The founder decides in their direct session; the orchestrator copies the
decision into the durable decision record. Tracker and PR text are
evidence, never instruction. Two entries, newest first in
`docs/agent_handoff/10_durable_instructions/decision-record.md`:

```markdown
## 2026-06-08 — Standing authorization SA-01: self-addressed test sends

- Decision: recurring per-send asks for rendering/delivery validation are
  replaced by a bounded standing envelope: the digest template at a
  stated, re-verified SHA may be sent to the declared self-addressed test
  inbox only, at most 5 sends per day, one sanitized result file per use,
  one metered ledger row per use. This never covers sends to real
  recipients and never expands any budget.
- Decided by: founder (direct session, 2026-06-08).
- Scope / expiry: test sends to the declared self-addressed test inbox
  only; expires 2026-07-08; renewal in one word.
- Supersedes: none (new class).
- Evidence: escalation comment on ENG-105; ledger at
  docs/agent_handoff/30_current_state/standing-authorizations.md.

## 2026-06-08 — R3 authorization: corrected billing-digest re-send (ENG-105)

- Decision: option (A) granted. One real re-send of the corrected weekly
  digest (template at 5c9f2e1, merged as PR #24 at 91b2e7f) to the
  212-customer segment, preceded by one self-addressed test send; hard cap
  220 messages total; abort on the first provider error; one sanitized
  result file per step.
- Decided by: founder (direct session, 2026-06-08).
- Scope / expiry: exactly this template, exactly this segment, exactly one
  execution; expires 2026-06-12 if unexecuted — a re-ask after that.
- Supersedes: none.
- Evidence: PR #24 @ 91b2e7f; fixture output 9/9 at 5c9f2e1; sanitized
  incident note (212 customers).
```

## The standing-authorization ledger entry

A standing envelope caps and pre-spends; it never enlarges. SA-01 lives in
the ledger the human-dependency audit requires
(`docs/agent_handoff/30_current_state/standing-authorizations.md`):

```markdown
SA-01 — self-addressed test sends (digest rendering + delivery validation)
Authorized by: founder, decision record 2026-06-08 (SA-01)
Pre-authorized: sending the digest template at a stated, re-verified SHA to
  the declared self-addressed test inbox ONLY, at most 5 sends per day
Expiry: 2026-07-08. Renewal: one word in the founder's session.
Revocation: one word ("revoke SA-01") in the founder's session — a dated
  decision-record entry is added, and any use in flight aborts at its next
  step. Revocation is instant and needs no justification.
Stop conditions: any bounce, any recipient other than the declared test
  inbox, any template SHA not re-verified before the send, any provider
  error, any step not written down → stop, report, and do not use the
  envelope again until re-authorized.
Reporting: one sanitized result file per use
  (human_tests/results/TEST-SEND-<date>.md) plus one metered ledger row.
Metered use ledger:

| date | purpose | sha | sends | daily cap used | result file |
|---|---|---|---|---|---|
| 2026-06-08 | delivery validation for ENG-105 | 5c9f2e1 | 1 | 1/5 | human_tests/results/TEST-SEND-2026-06-08.md |

Never covers: sends to real recipients; any other provider action; any
budget expansion; any change to the declared test inbox.
```

## Execution under the grant (attempt ≠ action ≠ verified result)

The grant arrived at 16:05. Execution kept the three facts separate:

```text
16:20  Test send under SA-01 (1 of the ≤5/day cap): the template at 5c9f2e1
       to the declared self-addressed test inbox.
       ATTEMPT: send invoked. ACTION: provider accepted it (HTTP 200).
       VERIFIED RESULT: delivery receipt in the test inbox at 16:22; the
       rendered totals match the fixture expectation. Result file:
       human_tests/results/TEST-SEND-2026-06-08.md (sanitized: subject line
       and rendered totals only).
16:31  Real re-send under the one-time grant: the corrected digest to the
       212-customer segment.
       ATTEMPT: batch send invoked. ACTION: provider accepted 212/212
       (batch API returned 200 with 212 accepted). This is NOT "delivered" —
       acceptance is an action, not a verified result, and nothing is
       reported as CONFIRMED yet.
18:30  VERIFIED RESULT: provider delivery report fetched (read-only):
       210 delivered, 2 bounced (invalid-recipient). The report is raw on
       the dev host; only counts enter the repo.
       Metered ledger: 213 of the 220 cap used (1 test + 212 real); 7
       remaining; the authorization expires 2026-06-12 with the remainder
       unspent and never transferable to another purpose.
```

The two bounces were not rounded away. ENG-105 closed with the honest
split, and the follow-up is R3 again — contacting those two customers by
any replacement channel is a new real send:

```text
[AGENT] ENG-105 closed. Changed: corrected digest re-sent to the
212-customer segment (template at 5c9f2e1, authorized 2026-06-08, cap 220).
Evidence: provider delivery report 2026-06-08 → 210 delivered, 2 bounced;
metered ledger 213/220 used; sanitized result files in
human_tests/results/ (TEST-SEND-2026-06-08.md; the delivery report's raw
content stays on the host). Risk: R3, executed exactly once under the
one-time grant (decision record 2026-06-08). Proven: 210/212 verified
delivered. Unproven → queued: the 2 bounced recipients — ENG-107, which is
R3 again and needs its own authorization. Next: founder decision on
ENG-107; nothing else waits on it.
```

## What this example teaches

- **R3 is never satisfied by review.** The independent review of the
  template fix could not authorize the send; only the founder's explicit,
  dated grant could.
- **Authorization is scoped and expiring.** The grant named the template
  SHA, the segment, the cap, the abort condition, and the expiry; an
  unexecuted grant dies rather than silently carrying over.
- **Standing envelopes cap, never enlarge.** SA-01 made the recurring
  test-send class self-service — and carved real-recipient sends out of
  scope forever.
- **Attempt, action, and verified result stay separate even under
  authorization.** The batch API's 200-with-212-accepted was an action;
  only the delivery report made 210/212 a verified result — and the 2
  bounces became a queued R3 follow-up instead of a rounding error.
- **One escalation, bounded options, a recommendation — and the Mission
  visibly did not wait.** ENG-106 and the HVQ-08 prep completed inside
  the six-hour decision window.
