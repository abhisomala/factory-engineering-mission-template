# Maturity statement

This is the template's honest self-assessment. It separates what is
**proven** from what is **unproven**, in the same spirit the template asks
of the agents that use it. It is a status record, not marketing, and it is
kept short on purpose. Treat `PROVEN` as "best evidence so far", not as a
guarantee.

As of: 2026-10-22.

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
  README contents tree matches the working tree and that internal file
  references resolve. It runs on this repository with no false positives.
  Its own passing and failing behavior is exercised by a negative test
  (a deliberately broken scratch copy) recorded in the Day 1 report.
- **Exercised its own R2 conditional-merge path.** The readiness check
  (`scripts/validate.py --adopted` plus `templates/readiness-checklist.md`)
  went through the complete process this template prescribes for
  verification-logic changes: implemented by one agent, independently
  reviewed by another (conditions 1–6 reproduced; condition 7 caught the
  checklist overclaiming what the code checks), corrected, re-reviewed
  to APPROVE, and merged — the full trail visible in PR #5 and the Day 2
  report (`agent_reports/2026-10-22.md`).

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
- **Continuous integration.** There is no CI pipeline yet; the
  self-validation script is run by hand, so nothing enforces that it stays
  green on every change.
- **End-to-end worked example.** The example queue and the example daily
  report are illustrative. They have not been walked through
  end to end against a live tracker and a real host-validation window.

## How to read this

Every `PROVEN` item above points at an artifact in this repository or a
recorded review, and every `UNPROVEN` item names a specific gap with a
concrete way to close it (measure a human-paced quickstart, onboard a
team, add CI, run the example end to end). When a gap closes, move the
item and date the change rather than deleting the record.
