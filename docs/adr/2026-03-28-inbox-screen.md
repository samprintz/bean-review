# Inbox Screen

`bean-review` originally required a single `.beancount` file as input.
In practice, imports are staged in a directory: each import file (CSV, PDF, …)
gets a `.beancount` counterpart produced by `bean-stage`.
Navigating that directory externally and invoking `bean-review` per file
adds friction to the review workflow.

## Decision

Accept a directory as the positional argument in addition to a single file.
When given a directory, open an Inbox Screen listing all import files,
with visual distinction between reviewable entries (`.beancount` present)
and pending entries (not yet staged).
Selecting a reviewable entry pushes the existing Transaction List Screen.

## Consequences

- A single invocation covers the entire review session without shell loops.
- Pending entries are surfaced in context, preparing for a future
  `bean-stage` trigger keybinding without requiring a new entry point.
