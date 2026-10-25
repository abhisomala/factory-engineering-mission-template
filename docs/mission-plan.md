# Mission plan — v0.1

This repository is being evolved into a production-ready public resource
through a bounded development mission. This file is the plan the
project's agents resume from, and a public record of how the template is
being improved. It follows the template's own rules: day-by-day status
lives in `agent_reports/`, this plan's status column is updated in the
same commit that completes a milestone, and old records are never
rewritten to look current.

As of: 2026-10-22 (milestone density expanded the same day at the
founder's direction — every item below has a user outcome; there is no
padded or manufactured work in this plan).

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

Changed 2026-10-23 (dated addendum; founder decision): the scheduled
morning automation (`mission-daily-milestone-run`, 09:00 local, created
2026-10-22 — see the Day 2 report) was deleted after its first run
failed partway: it authored and opened Day 3's schema PR, then stopped
before review, merge, and the daily report (the full account is in the
Day 3 report). Its absence was verified on 2026-10-23 (founder
session; re-verified the same day against the platform's automation
list — no local, no cloud automations). The founder chose to prompt the
Mission daily instead. Each prompted session — like any fresh session —
resumes the same way: reconcile state, delegate bounded task
contracts, validate, merge per risk tier, and file the dated report in
`agent_reports/`.

Each milestone carries 4–6 real PRs from this plan's lists. Authoring
runs in parallel across non-conflicting surfaces, using isolated
worktrees when the main checkout is busy; merges serialize, because
every new file must be registered in the README contents tree — one
README-touching PR merges at a time. That serialization is a recorded
throughput lesson for the README redesign to address (for example,
directory-level tree entries for deep trees).

## Milestones

| Day | Milestone | Ships | Status |
|---|---|---|---|
| 1 | Self-validation + honest maturity statement | `scripts/validate.py` (positive + negative tested), `docs/maturity.md`, "Verifying your copy" README section | DONE 2026-10-22 (PR #1) |
| 2 | Cold-start adoption, measured | cold-start test by a zero-context reader; quickstart fixes + measured duration claim; a new readiness-checklist template; "Is this for you?" README section; this mission plan committed | DONE 2026-10-22 (PRs #2, #3, #4, #6; readiness checklist + `--adopted` mode merged via PR #5 through the full R2 conditional-merge path: independent review FIX-REQUIRED → wording fixes → re-review APPROVE → merge) |
| 3 | Worked examples (4–6 PRs) | full R1 + R2 lifecycle example; R3 authorization example; host-validation worked example; validator schema checks for the examples; a one-line-per-file reference index | DONE 2026-10-23 (examples PR #8; schema checks PR #11 through the full R2 path — independent review APPROVE at b88fb8f, all seven conditions re-derived by a separate session; reference index PR #12). Five format-gap findings reconciled against merged main with dispositions in the Day 3 report (queued Days 4–8) |
| 4 | Automated trust (5–6 PRs; R2 — independent review before merge) | CI workflow running the validator; privacy-scan script with a planted-token self-test; PR template enforcing the Changed/Evidence/Risk reporting contract; markdown lint plus the fixes it flags; a one-command check script; README badge once CI is green | DONE 2026-10-24 (PRs #15–#21; all six planned deliverables shipped, plus a PR closing the runner's review-named coverage gaps). Every PR was authored by one session and independently reviewed by a different one: 11 review posts, 5 FIX-REQUIRED verdicts across PRs #16–#19, then APPROVE. Four defects were caught in the template's own verification code before merge — a scanner echoing secret-shaped filenames (PR #16), fence matching that could report a broken document clean (PR #17), a runner leaking the operator's absolute path behind a regression assertion that masked the very string it checked for (PR #19), and PR-template wording that did not preserve the automated-test red line (PR #18). Regression suite 26 → 57 tests; two Day 3 gap findings closed (gap 3, tracker-issue body; gap 5, synthetic-path rule for adopters) |
| 5 | README redesign I — design agent (4–5 PRs) | redesign spec built from the cold-start evidence; a glossary defining every term once; terminology consistency pass across the docs; long-section split-out prep | PARTIALLY DONE 2026-10-22 (spec + both diagram-style samples prepared by the design agent; founder's style pick pending; glossary, terminology pass, and split-out prep remain) |
| 6 | README redesign II (4–5 PRs) | new diagram set in the founder-selected style; concise rewrite (target about 1,200 words, from about 2,700); validator coverage for the new assets; honest readability metrics recorded | PLANNED (blocked on the Day 5 style pick) |
| 7 | README redesign III (4 PRs) | understander round-1 fixes (a fresh zero-context reader tested against the spec's outcome questions); round-2 fixes until the 60-second and 5-minute outcomes hold; independent reviewer fixes; redesign retrospective | PLANNED |
| 8 | Founder sign-off + maintainer story (5–6 PRs) | founder approves the rendered README before merge; contributor guide (`CONTRIBUTING.md`); learning log seeded with the true dated history; decision-record template; security policy; code of conduct | PLANNED |
| 9 | v0.1 freeze (4 PRs) | fresh full-repo independent review (usability, principle preservation, privacy); fixes; a dated changelog of everything shipped; v0.1 scope + limitations statement; final consistency sweep | PLANNED |
| 10 | Real-use handoff (4–5 PRs) | dogfood protocol + next-mission doc; friction-log format for the first real adopter; final polish from the learning log; final report + honest-history audit (every PR body walked against its diff) | PLANNED |

## Founder gates

- Day 5: pick the diagram style — both style samples were prepared
  early, on 2026-10-22, by the design agent (restructured Mermaid vs
  hand-authored SVG); the pick is pending and blocks Day 6.
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
