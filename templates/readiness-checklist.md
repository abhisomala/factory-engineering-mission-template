# Adoption readiness checklist

For a repository that has adopted this template (README quickstart
steps 1–5 complete). Readiness has two halves, and this checklist keeps
them honestly separated:

- **Machine checks** — `python3 scripts/validate.py --adopted` proves
  the in-repo bootstrap outputs exist and are internally consistent.
- **Human gates** — the external setup that no repo-local check can
  certify. A human verifies each one once, on the platform.

## Part 1 — machine checks: what `--adopted` proves

Run from your repository root:

```text
python3 scripts/validate.py --adopted
```

It exits 0 only when every check passes:

| Check | What it proves | What it does NOT prove |
|---|---|---|
| Runtime directories exist (`docs/agent_handoff/`, `human_tests/`, `agent_reports/`) | the three write-into directories were created | nothing about their content quality |
| Day-one bundle files non-empty (`00_README.md`, `HOST_VALIDATION_QUEUE.md`, `MANIFEST.md`, `10_durable_instructions/`) | the four files exist non-empty | that their placeholders were filled in, or that their content is *correct* for your project — only the HVQ `[DATE]` placeholder (HVQ-shape row) and the manifest entries (MANIFEST-hashes row) are content-verified |
| `human_tests/PENDING.md` exists | the host-evidence boundary was created | that any request block in it is well-formed |
| HVQ shape (dated status block filled + table header present) | the two schema header elements are present: a `## Dated status block` header with the `[DATE]` placeholder gone, and a `\| ID \|` table header line | that the rest of the `.factory/skills/host-validation/SKILL.md` §5 schema (column set, row rules) is followed, or that the queued items are the *right* items |
| MANIFEST hashes (every listed entry matches its file; `00_README.md` and `HOST_VALIDATION_QUEUE.md` covered) | every listed hash line matches its file on disk (works with `sha256sum` and `shasum -a 256` output), and the two day-one files are covered — entries for `10_durable_instructions/` and other bundle files are optional, verified when listed | tamper detection against a determined attacker, or the integrity of any *unlisted* bundle file |
| AGENTS.md risk surfaces (placeholder block replaced) | you replaced the template's R2/R3 placeholder with your own definitions | that your definitions are good — a human reads them |

## Part 2 — human gates: what only you can verify

Each of these is **external** to the repository. No script here can see
your forge settings, your credential store, or your tracker.

- [ ] **`main` is protected.** The ruleset that rejects non-PR pushes to
  `main` exists, applies to every credential including the agents', and
  has no bypass entry for agent identities.
- [ ] **The agent credential's scope is what you intended.** In your
  forge's credential settings, the fine-grained token lists exactly the
  permissions you chose (e.g., contents/PRs/issues read-write, metadata
  read) and nothing administrative.
- [ ] **No token is embedded in the remote URL.** `git remote -v` shows
  a clean URL; the credential helper supplies the token without
  printing, logging, or persisting it in the repository.
- [ ] **Tracker labels exist.** `needs-machine`, `needs-human`,
  `needs-founder`, `R0`–`R3` (and any `needs-<host>` / `metered`) are
  present in your tracker.
- [ ] **The Mission starts and responds.** With
  `templates/mission-start-prompt.md` and your objective, the
  orchestrator reconciles state and proposes the first three tasks with
  risk tiers and evidence bars.
- [ ] **A human read your R2/R3 definitions.** The machine check only
  proves the placeholder was replaced; the definitions themselves need
  a human reader.

When every box holds, record the completion (dated) in the durable
decision record
(`docs/agent_handoff/10_durable_instructions/decision-record.md`) — that
record, not this template, is your readiness evidence.
