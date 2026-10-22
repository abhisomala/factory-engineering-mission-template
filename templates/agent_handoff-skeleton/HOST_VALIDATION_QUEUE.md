# Host validation queue (durable)

> Starter copied from
> `templates/agent_handoff-skeleton/HOST_VALIDATION_QUEUE.md`. Replace
> the placeholders and delete this note. The queue's rules live in
> `.factory/skills/host-validation/SKILL.md` (§3: the
> `human_tests/PENDING.md` request blocks; §4: the status vocabulary;
> §5: this schema).

## Dated status block — [DATE] (LATEST)

[WHAT CHANGED IN THIS WINDOW AND WHY — a new dated block supersedes the
older blocks, which stay below as history; never rewrite an old block]

| ID | Description (task/PR, commands, scope) | Status | Priority | Head SHA | Requested | Result |
|---|---|---|---|---|---|---|

One row per check, appended below this table — never delete or rewrite
an old row; add a dated status note instead. Statuses: `READY`,
`LEASED`, `IN_REVIEW`, `PASS`, `FINDING`, `INCOMPLETE`, `INCONCLUSIVE`,
`UNEXECUTED_ON_<HOST>`, `BLOCKED`, `DONE`.
