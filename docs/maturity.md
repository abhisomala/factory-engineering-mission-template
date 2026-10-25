# Maturity statement

This is the template's honest self-assessment. It separates what is
**proven** from what is **unproven**, in the same spirit the template asks
of the agents that use it. It is a status record, not marketing, and it is
kept short on purpose. Treat `PROVEN` as "best evidence so far", not as a
guarantee.

As of: 2026-10-24.

## Proven

- **Extracted from a real system.** The operating model — risk tiers,
  evidence policy, independent review, host validation, and the
  human-dependency audit — was extracted from a real, long-running
  autonomous engineering project and then generalized for publication.
  It is not a design written from scratch.
- **Survived one independent usability review before publication.** The
  pre-publication copy was reviewed end to end by a reviewer who did not
  author it; the 16 findings from that review were fixed before release.
- **Structurally self-checked.** `scripts/validate.py` verifies that the
  README contents tree matches the working tree, that internal file
  references resolve, and — since 2026-10-23 (PR #11) — that the three
  shipped worked examples keep their required structured artifacts. It
  runs on this repository with no false positives. Its passing and
  failing behavior is exercised by a deliberately broken scratch copy
  (Day 1 report) and, since 2026-10-23, by offline regressions
  (`scripts/test_validate.py`, PR #11) covering both modes, the original
  gates, and every required example field — 57 of them as of 2026-10-24.
- **Continuous integration — CLOSED 2026-10-24 (PRs #15, #17–#20); it was
  listed as unproven on 2026-10-23.** A workflow at
  `.github/workflows/validate.yml` runs the structural self-validation,
  the regression suite, the privacy scan, and the markdown lint on every
  push to `main` and every pull request, on `ubuntu-latest` and
  `macos-latest`, with `contents: read`. Its first runs are green on both
  runners. Scope, stated precisely: CI checks out a **merge ref**, so a
  green run is evidence for the merged tree rather than proof that a
  branch tip executed; exact-head behavior rests on the recorded local
  runs in the daily reports.
- **Its own output is checked for leaks.** Since 2026-10-24 (PR #16) a
  privacy scan covers service-token shapes, PEM blocks, credential
  assignments, email addresses, and absolute home paths across every
  committable file, including the runtime record directories, with
  planted-token self-tests pinning both its rules and its redaction; and
  the scripts themselves no longer print the operator's absolute
  repository root (PR #19 fixed the last two prints). Two review rounds
  found real leaks here — a scanner that echoed a secret-shaped filename,
  and a runner whose leak was hidden by a regression that masked the very
  string it claimed to assert was absent. Both are fixed and both are now
  tested against raw, unmasked output.
- **A structural markdown lint covers every markdown file** (PR #17):
  fence balance (a fence closes only on the same character, at least the
  same length, with nothing after it), heading-level jumps, the one-H1
  rule with the dated-record exemption, trailing whitespace on prose, and
  final-newline hygiene. It flagged three real defects on its first run —
  including the orchestrator droid's own file, which had no H1 — and all
  three were fixed in the PR that introduced it.
- **The reporting contract is enforced by artifact, not memory.** Since
  2026-10-24 (PR #18) a PR template asks every change for Changed,
  Evidence, Risk, proven-vs-unproven, and Next, with the provenance
  fields `docs/evidence-policy.md` requires for a PROVEN claim, and it
  states the automated-test red line as a categorical prohibition that
  authorization cannot waive — wording a reviewer caught as too loose in
  the first version. The canonical tracker-issue body ships as
  `templates/tracker-issue.md`, closing a Day 3 gap finding.
- **One command runs all four checks** (`python3 scripts/check.py`,
  PR #19): it reports PASS / FAIL / ERROR per check, keeps running after
  a failure so one pass shows every failure, and exits non-zero if any
  check did not pass — including the ERROR case where a check could not
  run at all (missing, not a regular file, unreadable, unstartable,
  timed out), which is never reported as a pass.
- **Exercised its own R2 conditional-merge path.** The readiness check
  (`scripts/validate.py --adopted` plus `templates/readiness-checklist.md`)
  went through the complete process this template prescribes for
  verification-logic changes: implemented by one agent, independently
  reviewed by another (conditions 1–6 reproduced; condition 7 caught the
  checklist overclaiming what the code checks), corrected, re-reviewed
  to APPROVE, and merged — the full trail visible in PR #5 and the Day 2
  report (`agent_reports/2026-10-22.md`). The same path was walked a
  second time for the worked-example schema checks (PR #11,
  2026-10-23): authored by one session, independently reviewed to
  APPROVE by another with all seven conditions re-derived (including
  adversarial mutation and sabotage probes), then merged.

## Unproven

- **Quickstart duration, human-paced.** Measured once (2026-10-22) by a
  zero-context agent reader: 7m03s for reading plus the executable local
  steps at machine speed, excluding the external platform steps (ruleset,
  credential, tracker labels, Mission start). A human-paced adoption —
  including those external steps — is still unmeasured. The cold-start
  run and its findings are recorded in the Day 2 report
  (`agent_reports/2026-10-22.md`).
- **Third-party adoption.** No external team has adopted the template, so
  there is no real-use data about how it behaves in another project.
- **Hosts other than macOS and Linux.** The checks and CI have run on
  macOS (Darwin 25.6.0) and on Ubuntu and macOS CI runners. Nothing has
  run on Windows: `UNEXECUTED_ON_WINDOWS`.
- **The runner's default timeout.** `scripts/check.py` declares a
  900-second per-check timeout; the timeout *branch* is tested with the
  constant set to one second. The shipped default has never been reached
  by a real slow check: `UNEXECUTED_AT_DEFAULT_TIMEOUT`.
- **Adopter-side surfaces of the Day 4 artifacts.** The PR template's
  pre-fill behavior in GitHub's web UI and acceptance of
  `templates/tracker-issue.md` in another tracker are both unobserved —
  `UNEXECUTED_ON_GITHUB_UI` and `UNEXECUTED_ON_ADOPTER_TRACKER`.
- **Residual coverage gaps in the check runner**, named by its PR #20
  review and queued rather than silently accepted: the shipped default
  timeout value is not asserted (only the timeout path), a start-failure
  ERROR in the first check position is not proven to continue through the
  rest of the run, and `main()`'s wiring of the output sanitizer is not
  pinned at the command line (only `make_sanitizer` itself is tested).
  Each was verified as correct in the shipped code by mutation probes
  that escaped the suite; they are missing tests, not observed defects.
- **End-to-end worked example.** Three worked examples have shipped
  since 2026-10-23 (PR #8: an R1+R2 lifecycle pair, an R3 authorization,
  a host-validation item), and their structure is machine-checked
  (PR #11) — but all three are synthetic by construction, and the
  checks prove shape, not outcomes. Nothing has been walked through
  end to end against a live tracker and a real host-validation window;
  the example queue and the example daily report remain illustrative.

## How to read this

Every `PROVEN` item above points at an artifact in this repository or a
recorded review, and every `UNPROVEN` item names a specific gap with a
concrete way to close it (measure a human-paced quickstart, onboard a
team, add CI, run the example end to end). When a gap closes, move the
item and date the change rather than deleting the record.
