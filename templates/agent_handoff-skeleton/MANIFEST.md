# Bundle manifest — integrity hashes

Starter copied from `templates/agent_handoff-skeleton/MANIFEST.md`.
Delete this paragraph when the entries below are real.

One line per bundle file: the output of `sha256sum <file>` run from the
repository root (Linux), or `shasum -a 256 <file>` on stock macOS, which
ships `shasum` instead of `sha256sum` — both write the same
`<64-hex-sha256>  <path>` line. Re-hash any entry whose file changed,
in the same commit as the change. A file cannot contain its own
checksum, so `MANIFEST.md` itself stays unlisted.

Entry format:

```text
<64-hex-sha256>  docs/agent_handoff/<file>
```

Entries — replace the placeholder line below with real hash lines:

[NO ENTRIES YET]
