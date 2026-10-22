# Worked example: a host-validation item, end to end

Some behavior can only be certified on a specific host — a real device, a
particular OS or assistive technology, a production or staging environment.
Nothing run anywhere else is evidence for that host, and unrun host cases
are `UNEXECUTED_ON_<HOST>` — never pass, never fail.

This example traces one host-validation queue item to completion, in the
same synthetic project as `examples/worked-example.md` — a web dashboard
everyone calls **the console**. It picks up exactly where the R2 example
stopped: the deploy-readiness gate change (ENG-102, merged at main 8f3a6b1
after a 7-condition review) was proven **at fixture level only**. A real
staging observation of the new gate is a different evidence class — the dev
host talks to a stubbed deploy service — so it was queued as HVQ-07 under
ENG-103 and never claimed by the R2 PR.

Every ID, SHA, date, count, and output below is synthetic and
self-consistent. The schema is
`.factory/skills/host-validation/SKILL.md`: §3 defines the request block,
§4 the status vocabulary, §5 the queue schema used below.

## 1. The queue rows (schema §5)

The queue file is `docs/agent_handoff/HOST_VALIDATION_QUEUE.md`, organized
under dated blocks (newest first; old blocks stay as history). The dated
block at the end of this story:

```markdown
## Dated status block — 2026-06-05 (LATEST)

HVQ-07 (ENG-103, the staging observation of the ENG-102 gate change) ran
in the staging window and returned PASS at the exact SHA; HVQ-08
(ENG-104, VoiceOver keyboard navigation) was requested for the next macOS
window and remains honestly unexecuted.

| ID | Description (task/PR, commands, scope) | Status | Priority | Head SHA | Requested | Result |
|---|---|---|---|---|---|---|
| HVQ-07 | Staging observation of the deploy-readiness gate (ENG-103, verifies ENG-102 merged at 8f3a6b1): deploy the two prepared scratch builds via the staging console UI, read the gate report panel; read-only except the two reversible scratch-surface deploys; no model calls; TEST- operator sign-in | DONE | P1 | 8f3a6b1 | 2026-06-04 | PASS 2026-06-05 → human_tests/results/HVQ-07.md |
| HVQ-08 | VoiceOver keyboard navigation of the saved-filters drawer (ENG-104): 6-step read-only UI walk; requires macOS + VoiceOver | UNEXECUTED_ON_MACOS | P2 | 8f3a6b1 | 2026-06-05 | — |

Dated status notes (append-only — old text stays as history):

- HVQ-07 — 2026-06-04: added. Status UNEXECUTED_ON_STAGING at head 8f3a6b1
  (the reproducer is recorded on the dev host; fixture runs there are not
  staging evidence and infer nothing).
- HVQ-07 — 2026-06-04: → READY. Request block written to
  human_tests/PENDING.md; prerequisites: staging TEST- operator sign-in
  and the two prepared scratch builds (hvq-07-scratch-a, hvq-07-broken-b).
- HVQ-07 — 2026-06-05: head re-verified before the window
  (git ls-remote origin main → 8f3a6b1, unchanged); a PASS at an older SHA
  would have been history, not evidence, and the row would have gone back
  to READY at the new SHA.
- HVQ-07 — 2026-06-05: operator ran the block verbatim → PASS at 8f3a6b1;
  sanitized result saved to human_tests/results/HVQ-07.md; status → DONE;
  ENG-103 closed CONFIRMED with the result pointer.
- HVQ-08 — 2026-06-05: added. Status UNEXECUTED_ON_MACOS at head 8f3a6b1.
  The CI run of the drawer (headless Linux) certifies nothing about
  VoiceOver; no inference from it. Queued for the next macOS window; not
  pass, not fail.
```

## 2. The request block (human_tests/PENDING.md, schema §3)

The request must be executable **verbatim** by a qualified operator who is
not an engineer — if a step is not written down, it does not happen. This
one needs no code checkout at all (it observes the deployed staging
environment, which removes the fresh-clone requirement by construction):
verify the deployed version instead.

```text
TEST ID: HVQ-07
REQUESTED BY TASK / PR: ENG-103 (verifies ENG-102, merged PR #22 at 8f3a6b1)
REQUIRED ENVIRONMENT: STAGING — the staging console environment: any
  machine with a browser, the staging admin console sign-in (TEST-
  operator account), and the deploy pipeline viewer. No checkout, no
  local build, no code tools.
BUILD / COMMIT: main @ 8f3a6b1 (verify in step 2 before doing anything
  else)
RECORDED REPRODUCER STATUS: UNEXECUTED_ON_DEVHOST — the gate's fixture
  suite passed on the dev host (53/53 at head b4e7c92); a real staging
  observation was never run from there and the fixtures certify nothing
  here.
WHY THE CURRENT HOST CANNOT CERTIFY IT: the dev host talks to a stubbed
  deploy service; only staging runs the real deploy pipeline the gate
  must observe.
PREREQUISITES / PERMISSIONS: staging TEST- operator account signed in;
  the two prepared scratch builds (labels hvq-07-scratch-a and
  hvq-07-broken-b) visible in the Deploy menu; Pages delete permission
  for cleanup (same account).
SAFE STEPS / COMMANDS: read-only except two reversible deploys on the
  declared scratch surface (the two hvq-07-* test pages). No model
  calls. No checkout needed — you observe the deployed environment.
  1. Sign in to the staging admin console with the TEST- operator
     account.
  2. Open Help → About. The version line must read exactly 8f3a6b1. If
     it reads anything else: STOP. Report INCOMPLETE with the version
     you saw. Do not run the rest.
  3. SUCCESS CASE: open Deploy → Staging. Select the build labeled
     hvq-07-scratch-a. Press Deploy. Wait for "finished". Open
     Readiness → Gate report. Copy the two summary lines (status=... and
     observed_version=...).
  4. FAILURE CASE: back in Deploy → Staging, select the build labeled
     hvq-07-broken-b (prepared to fail its rollout). Press Deploy. Wait
     for "finished". Open Readiness → Gate report. Copy the same two
     summary lines.
  5. CLEANUP: open Pages. Delete hvq-07-scratch-a and hvq-07-broken-b.
     Sign out.
EXPECTED EVIDENCE: step 2 version = 8f3a6b1; step 3 lines show
  status=CONFIRMED and observed_version matching the scratch-a build;
  step 4 lines show status=UNCONFIRMED and
  reason=observed_version_unchanged — the gate must NOT confirm a deploy
  whose version did not change. Paste exactly the copied lines, nothing
  else, into the result file.
PRIVACY NOTES: the gate report lines contain only build labels, version
  strings, and status words — no customer data. The scratch pages contain
  the word TEST and nothing else. Do not paste screenshots, URLs with
  query strings, or account names.
CLEANUP / RESTORE: both scratch pages deleted in step 5; nothing else
  changes on staging.
RESULT FILE: human_tests/results/HVQ-07.md
```

## 3. The operator's run note

The operator is a qualified non-engineer. The block was designed so the
returned evidence is sanitized by construction — the only material the
operator ever copies is the two report lines per case, which contain
labels, versions, and status words:

```text
Operator note (2026-06-05): ran the HVQ-07 block verbatim from
human_tests/PENDING.md, all five steps in order. Step 2: the About panel
showed 8f3a6b1, so I continued. Success case finished and the gate report
showed CONFIRMED. Failure case finished and the gate report showed
UNCONFIRMED. No prompts appeared, nothing unexpected showed up on screen,
no stop condition hit. Deleted both scratch pages and signed out. I copied
only the report summary lines into the result file, as instructed.
```

## 4. The sanitized result file (human_tests/results/HVQ-07.md)

Exactly the evidence the request demanded, nothing raw. The full report
panel capture stays on the validation host in a dated raw-run directory;
its checksum is recorded here so the record is verifiable without exposing
content that never needed to leave the host:

```markdown
# HVQ-07 — staging deploy-readiness gate observation (sanitized result)

- Status: PASS
- Ran on: STAGING (per REQUIRED ENVIRONMENT), 2026-06-05
- Build / commit: main @ 8f3a6b1 (verified at step 2: About panel read
  8f3a6b1)
- Executed by: authorized operator (non-engineer), block run verbatim
- Raw capture (full gate report panel text for both cases) preserved on
  the validation host in the dated raw-run directory; not committed.
  sha256 of raw capture:
  8cbc9616dbaf51e1eff5cd16e2fb9403a5533de47d5b9d27866428e7846eb17b

## Observed evidence (exactly the requested lines; nothing else)

Success case (build hvq-07-scratch-a):

  status=CONFIRMED observed_version=2.4.1-hvq07a

Failure case (build hvq-07-broken-b):

  status=UNCONFIRMED reason=observed_version_unchanged

## Pass criteria check

- Version at step 2 = 8f3a6b1: met
- Success case: gate reported CONFIRMED with the observed version
  matching the scratch-a build: met
- Failure case: gate did NOT confirm a deploy whose version did not
  change (UNCONFIRMED, observed_version_unchanged): met

## Notes

- No stop conditions hit; no unexpected content; cleanup completed (both
  scratch pages deleted; signed out)
- This PASS applies to exactly main @ 8f3a6b1. If the head moves, this
  result is history, not evidence for the new head.
```

## 5. Recording it: queue transition and tracker close

Back in the queue, the HVQ-07 row moved through its dated notes
(`UNEXECUTED_ON_STAGING` → `READY` → `PASS` → `DONE`, shown in section 1)
with the result pointer in the Result column. The queue row's status
vocabulary is the host-test vocabulary (`PASS`); `CONFIRMED` is the
task/work vocabulary, and it belongs to the tracker issue the row
certifies. ENG-103 closed with the standard comment contract:

```text
[AGENT] ENG-103 closed. Changed: nothing — this issue existed to hold the
staging evidence bar for ENG-102's gate change. Evidence: HVQ-07 executed
by the operator on STAGING at main @ 8f3a6b1 → PASS; sanitized result at
human_tests/results/HVQ-07.md; queue row → DONE with the result pointer
(docs/agent_handoff/HOST_VALIDATION_QUEUE.md, dated block 2026-06-05).
Risk: none new — observation only; the risk lived in ENG-102 and was
reviewed there. Proven: the new gate confirms a real successful staging
deploy and refuses a stuck rollout, on the required host, at the exact
SHA. Unproven: nothing on this item's bar. Next: HVQ-08 in the next macOS
window (still UNEXECUTED_ON_MACOS).
```

One dated addendum line in the durable context:

```text
- 2026-06-05: HVQ-07 PASS on STAGING at main 8f3a6b1 (result:
  human_tests/results/HVQ-07.md); ENG-103 closed CONFIRMED — the deploy
  gate is now staging-observed, not only fixture-proven. HVQ-08 still
  UNEXECUTED_ON_MACOS. Verify before use.
```

One line of that day's daily report (agent_reports/2026-06-05.md):

```text
- HVQ-07 run by the operator on STAGING at main 8f3a6b1 → PASS; sanitized
  result human_tests/results/HVQ-07.md; queue row → DONE; ENG-103 closed
  CONFIRMED. HVQ-08 remains UNEXECUTED_ON_MACOS (queued for the next
  macOS window; not pass or fail).
```

## 6. The neighboring row that stays honestly unexecuted

HVQ-08 has not run, and the queue says so in the only honest way:
`UNEXECUTED_ON_MACOS`. That status means precisely:

- The drawer's CI run on headless Linux says nothing about VoiceOver, and
  no inference is drawn from it.
- The item is queued with its prerequisites (a Mac with VoiceOver, the
  six-step block, an operator at the keyboard), not failed, not stale,
  not forgotten.
- The Mission did not idle: while HVQ-08 waits for its window, the R3
  authorization lane in `examples/worked-r3-example.md` and ordinary R0/R1
  work continued.
- When the window opens, the row goes `READY` at a re-verified SHA, the
  block runs verbatim, and the result — whatever it is — is one of the
  §4 statuses. `PASS` is earned in the window, never assumed outside it.

## What this example teaches

- The boundary is one-way and narrow: precise request in
  `human_tests/PENDING.md` → operator runs it verbatim on the required
  host → sanitized result file out. Raw material never crosses.
- A request written for a non-engineer is also a request whose returned
  evidence is sanitized by construction — the two summary lines were safe
  to paste before anyone had to sanitize them.
- The exact-SHA rule is enforced twice: the operator verifies the version
  before running, and the orchestrator re-verifies the head before the
  window. A PASS at a moved SHA is history.
- `UNEXECUTED_ON_<HOST>` is a first-class, honest status — not a gap to
  paper over, and never a pass or a fail.
- The row's statuses and the issue's statuses are different vocabularies
  doing different jobs: the row says what the host run returned; the
  tracker issue is what becomes CONFIRMED.
