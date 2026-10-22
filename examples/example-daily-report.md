# Example: daily agent report

One dated file per day with substantive work:
`agent_reports/YYYY-MM-DD.md`. The report is written for the founder to
skim in one screen and trust: every claim has a pointer, and what was
*not* verified is stated as plainly as what was. All content below is
generic.

---

```text
DATE: 2026-01-15
ACTIVE OWNER / TASK: Engineering Manager / ENG-42 notification-summary v2 (R1)

REPO / BRANCH / COMMIT: <repo> / agent/2026-01-15/notification-summary-v2 (from main <sha>)

COMMITS / PRS: 1 commit; draft PR #12 to main (not merged)

EVIDENCE PRODUCED:
- summary truncation fix + 6 new unit tests (all pass at head <sha>)
- docs/agent_handoff/30_current_state/gates.md updated (dated addendum)
- HOST_VALIDATION_QUEUE.md: HVQ-12 added (READY, P1, head <sha>)

GATES / RESULTS:
- repository test suite at head vs base (same host): same pass set
  before/after (14/14), no regressions; new tests 6/6 PASS on CI (Linux)
- mail-client correctness: UNEXECUTED_ON_MACOS — queued as HVQ-12, not
  claimed

CLAIMS NOT VERIFIED:
- real mail-client rendering at 10k-message mailboxes (needs HVQ-12)
- notification latency under load (no benchmark budget requested)

RED-LINE STATUS: none tripped; none outstanding for this surface

HOST/HUMAN TESTS REQUESTED OR RECEIVED: HVQ-12 requested in
human_tests/PENDING.md (3 commands, read-only, no model calls)

EXTERNAL PROVIDERS / COST / CALL USAGE: none (fixture-only work)

HUMAN REVIEW TIME ESTIMATE: PR #12 ≈ 10–15 min

REVIEW BACKLOG: 1 draft PR (within the ~2-PR backpressure cap)

BLOCKERS: none on ENG-42; ENG-46 still awaits the founder budget
decision (escalated with options yesterday; safe work continuing)

NEXT ACTION: independent review of PR #12 (different worker); HVQ-12 in
the next host window
```

---

What makes this report trustworthy (and what reviewers check first):

- It separates what ran on CI from what can only be certified on a host,
  and refuses to blur them (`UNEXECUTED_ON_MACOS`, not "tested").
- It names its own unverified claims before anyone has to ask.
- It quantifies the human cost it is about to impose (review minutes).
- It ends with one concrete, safe next action — and shows the Mission
  kept moving on everything that was not blocked.
