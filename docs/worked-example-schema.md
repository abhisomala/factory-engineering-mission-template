# Worked-example structural checks

Plain `python3 scripts/validate.py` retains the README tree and inline
reference checks and adds one schema check for all three worked examples.
The schema is deliberately narrow: it reads the examples' existing
Markdown format, not arbitrary Markdown or an adopted project's records.
The implementation is `scripts/worked_examples.py`.

## What must be present

Required sections must occur once, with nonempty bodies. Required artifacts
must be nonempty fenced blocks **inside their own section**; mentioning a
field elsewhere in the document cannot supply it. Backtick and tilde fences
are supported; an unclosed fence fails. Section titles are structural keys,
including the existing numbered lifecycle steps; changing them requires a
schema change and review.

- **R1/R2 lifecycle** (`examples/worked-example.md`): both task sections
  need a tracker artifact (issue title, State, Labels, Body, acceptance
  bullets), all 21 named fields from `templates/task-contract.md`, the 13
  worker-handoff subsections, and the five branch/provenance fields.
  Each needs a merge artifact with commit and PR headers, followed by
  closing-comment, addendum, and daily-report fenced artifacts. The closing
  comment carries Changed/Evidence/Risk/Proven/Unproven/Next labels.
  R2 additionally needs a review artifact with seven numbered, named
  conditions, a PASS/FAIL plus evidence text for each, a verdict from the
  review vocabulary, and Next.
- **R3 authorization** (`examples/worked-r3-example.md`): the escalation
  fields, two dated decision sections (one-time and standing grants), and
  Decision/Decided by/Scope and expiry/Supersedes/Evidence fields in each.
  The ledger requires authorizer, pre-authorized scope, expiry, revocation,
  stop conditions, reporting, and exclusions fields, plus its six-column
  metered-use table. Execution needs timestamped material with labeled
  ATTEMPT/ACTION/VERIFIED RESULT records and a separate closing-comment
  artifact. These are labels and record shapes, not permission checks.
- **Host validation** (`examples/worked-host-validation.md`): a dated queue
  section and seven-column queue table; all 12 request fields from the
  host-validation skill; an operator-note artifact; and a sanitized-result
  artifact. The latter needs Status/Ran on/Build and commit/Executed by
  fields, a 64-hex checksum-shaped value, observed-evidence/pass-criteria/
  notes subsections, and two status plus version-or-reason evidence lines.
  Closing-comment, addendum, and daily-report artifacts are also required.

Line-based fields must occur once with a nonempty value; values may wrap
across lines and contain colons. Table headers must match the existing
column names, followed by a separator and at least one data row with every
cell filled. Tables are contiguous pipe-delimited lines; escaped pipes
are supported. No semantic interpretation of table cells is performed.
Diagnostics identify the example path and missing or malformed structure.

## What a PASS does not mean

**All three examples are synthetic.** Their embedded commands, paths,
authorizations, reviews, counts, SHAs, checksums, and results are illustrative.
The validator never executes embedded commands, follows artifact paths, or
contacts a provider or host. No runtime evidence files need to exist.

These checks do **not** establish factual accuracy, prose quality, valid
authorization, review independence, checksum integrity, chronological or
cross-example consistency, outcome arithmetic, safe operator steps, or real
host provenance. A checksum-shaped string is not a verified raw capture.
A filled evidence field is not an evidence artifact. A PASS here cannot
certify staging, macOS, delivery, a merge, or any other real outcome.
Those still require the evidence policy, founder grants, independent
review, and actual host-validation process.

`--adopted` remains a separate six-check bootstrap-readiness mode. It does
not run the worked-example schema or certify the external readiness gates.
Neither mode replaces human review.

## Authoring your own synthetic material

The plain-mode reference check scans prose backtick spans in every
markdown file, examples included. A span that looks like a
repo-relative path is tolerated only in two shapes: a documented
runtime prefix (`docs/agent_handoff/`, `human_tests/`, `agent_reports/`
— reported as runtime, never failed), or a first segment that is not a
top-level entry in the repository (the shipped examples' synthetic
project paths rely on this). A fictitious span that borrows a real
top-level first segment (for example `docs/`) is checked and fails if
the file does not exist. This is a shape rule for authored prose, not
a privacy or permission check.

## Repeatable regressions

```text
python3 scripts/test_validate.py
```

This standard-library-only suite creates disposable copies of this
repository's README-registered files in temporary directories, not ignored
local data. It checks the shipped positive
examples, removes each required contract/request field and other focused
structures independently, verifies failure diagnostics and CLI exit codes,
and exercises the original tree/reference exclusions and adopted-mode
positive and negative outcomes (including both manifest hash formats).
It never adopts or modifies the source checkout, executes sample commands,
or performs external side effects. A deliberate positive case changes a
synthetic outcome without failing: this records the semantic limitation,
not a claim that the altered story is correct.
