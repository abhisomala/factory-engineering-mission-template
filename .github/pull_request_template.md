# [AGENT] <One-line summary of the change>

<!-- Agent-authored PRs: prefix BOTH the title and this body summary line
with [AGENT]. Keep every section below; delete these comments before
requesting review. Never paste secrets, .env values, absolute home paths,
or raw private evidence — reference the sanitized file under
human_tests/results/ instead. -->

## Changed
<!-- Files and commits, one line each, plus the risk tier. -->

## Evidence
<!-- The exact commands run and their results, with the four provenance
     fields docs/evidence-policy.md requires for a PROVEN claim: the
     artifact, the host it ran on, the commit SHA, and the date. Label
     local runs at this head separately from CI results, and say plainly
     when a CI run checked a merge ref rather than this exact head.
     "Code written" is not evidence. -->

## Risk
<!-- R0–R3 per docs/risk-model.md, plus the residual risk after this change. -->

## Proven vs unproven
<!-- Two explicit lists. Every PROVEN item names its artifact, host, SHA,
     and date. Unrun host cases are UNEXECUTED_ON_<HOST> — never pass,
     never fail. Synthetic, fixture, or wrong-host results are never
     target-host evidence. A PR that hides an unproven area has failed
     review regardless of what its tests show. -->

## Next
<!-- One concrete next step, and the human gate this opens, if any. -->

## Checklist

- [ ] `python3 scripts/validate.py`, `python3 scripts/test_validate.py`, `python3 scripts/privacy_scan.py`, and `python3 scripts/md_lint.py` pass at this head
- [ ] No test, gate, benchmark, or acceptance bar was weakened to obtain a pass
- [ ] R2 (verification, safety, privacy, credentials, telemetry): a reviewer who did not author the change recorded APPROVE
- [ ] R3 (real external side effects): founder authorization was recorded before execution, outside automated tests
- [ ] No real external side effect ran inside an automated test — this is a categorical red line, not something authorization can permit
- [ ] No secrets, credentials, private data, or absolute home paths appear in the diff or this body
- [ ] Affected checks were re-run at the exact before/after SHAs, and the tracker issue links this PR
