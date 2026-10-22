# Mission plan — v0.1

This repository is being evolved into a production-ready public resource
through a bounded development mission. This file is the plan the
project's agents resume from, and a public record of how the template is
being improved. It follows the template's own rules: day-by-day status
lives in `agent_reports/`, this plan's status column is updated in the
same commit that completes a milestone, and old records are never
rewritten to look current.

As of: 2026-10-22.

## Standing boundaries (from the founder)

- Validated, reviewable changes only; small coherent PRs; never weaken
  the template's safety or evidence principles.
- No releases, tags, GitHub settings changes, or external announcements
  without founder approval.
- All agent GitHub text prefixed `[AGENT]`; agent commit identity;
  PRs only — never push directly to `main`, never force-push.
- Public content stays free of private identifiers: project names,
  personal names, source-project SHAs, local filesystem paths, emails,
  secrets.
- Founder gates pause only their own lane; agents continue safe,
  non-conflicting work meanwhile.

## Cadence

A scheduled automation runs each morning (09:00 local) and executes the
next incomplete milestone end to end: reconcile state, delegate
bounded task contracts, validate, merge per risk tier, and file the
dated report in `agent_reports/`. Any session — scheduled or fresh —
resumes the same way.

## Milestones

| Day | Milestone | Ships | Status |
|---|---|---|---|
| 1 | Self-validation + honest maturity statement | `scripts/validate.py` (positive + negative tested), `docs/maturity.md`, "Verifying your copy" README section | DONE 2026-10-22 (PR #1) |
| 2 | Cold-start adoption, measured | cold-start test by a zero-context reader; quickstart fixes + measured duration claim; a new readiness-checklist template; "Is this for you?" README section; this mission plan committed | IN PROGRESS |
| 3 | Worked examples | full R1 + R2 lifecycle example; R3 authorization example; validator schema checks | PLANNED |
| 4 | Automated trust | CI workflow running the validator; privacy-scan script with a self-test; link lint. Touches verification gates, so independent review before merge | PLANNED |
| 5 | README redesign I (design agent) | redesign spec built from the cold-start evidence; terminology pass; two diagram-style options prepared for the founder's pick | PLANNED |
| 6 | README redesign II | new diagram set (founder-selected style); concise rewrite; validator coverage for the new assets | PLANNED |
| 7 | README redesign III | understander cold-read fixes; independent-review fixes; iterate until clean | PLANNED |
| 8 | Founder sign-off + maintainer story | founder approves the rendered README before merge; contributor guide (`CONTRIBUTING.md`); learning log; decision-record template | PLANNED |
| 9 | v0.1 freeze | fresh full-repo independent review (usability, principle preservation, privacy); fixes; v0.1 scope + limitations statement | PLANNED |
| 10 | Real-use handoff | dogfood protocol + next-mission doc; final polish; final report + honest-history audit | PLANNED |

## Founder gates

- Day 5: pick the diagram style (options presented as rendered samples).
- Day 8: approve the redesigned README before it merges.
- Any release, tag, GitHub settings change, or external announcement.

## Resumption rules (any fresh session)

1. Read `AGENTS.md`, this file, the newest `agent_reports/` entry, and
   `docs/maturity.md`.
2. Check git state (status, HEAD, open PRs) and run
   `python3 scripts/validate.py` — it must be green before building.
3. Continue the first INCOMPLETE milestone. Never skip ahead while one is
   unfinished; never duplicate in-flight work.
4. Stop at founder gates with the decision request recorded in the day's
   report; continue safe parallel work meanwhile.
