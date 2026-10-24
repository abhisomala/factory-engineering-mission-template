# <One-line summary of the change>

<!-- Agent-authored PRs: prefix the TITLE with [AGENT]. Keep every section
below; delete these comments before requesting review. Never paste secrets,
.env values, absolute home paths, or raw private evidence — reference the
sanitized file under human_tests/results/ instead. -->

## Changed
<!-- Files and commits, one line each, plus the risk tier. -->

## Evidence
<!-- The exact commands run and their results, at the head SHA you are
     submitting. "Code written" is not evidence. -->

## Risk
<!-- R0–R3 per docs/risk-model.md, plus the residual risk after this change. -->

## Proven vs unproven
<!-- Two explicit lists. Unrun host cases are UNEXECUTED_ON_<HOST> — never
     pass, never fail. Synthetic, fixture, or wrong-host results are never
     target-host evidence. -->

## Next
<!-- One concrete next step, and the human gate this opens, if any. -->

## Checklist

- [ ] `python3 scripts/validate.py`, `python3 scripts/test_validate.py`, `python3 scripts/privacy_scan.py`, and `python3 scripts/md_lint.py` pass at this head
- [ ] No test, gate, benchmark, or acceptance bar was weakened to obtain a pass
- [ ] R2 (verification, safety, privacy, credentials, telemetry): a reviewer who did not author the change recorded APPROVE
- [ ] R3 (real external side effects): founder authorization was recorded before execution, including inside tests
- [ ] No secrets, credentials, private data, or absolute home paths appear in the diff or this body
- [ ] Affected checks were re-run at the exact before/after SHAs, and the tracker issue links this PR
