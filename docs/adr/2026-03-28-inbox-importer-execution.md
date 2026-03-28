# Inbox Importer Execution

The inbox screen surfaces pending files (not yet transformed to `.beancount`).
Without an in-app trigger, the user must leave the TUI, run the importer manually,
and relaunch — breaking the review flow.

## Decision

Add two import actions to the Inbox Screen:

- Import the focused file (passes the file path to the import command).
- Import all pending files (passes the inbox directory).

The import command is run via subprocess in a background thread.
The list refreshes automatically on completion.
Triggering import on an already-imported file requires confirmation to prevent
accidental overwrites.

Both actions share `import_cmd` as their base configuration key.
`import_all_cmd` can override the bulk-import command independently
(e.g. to pass different flags or use a different tool).

## Consequences

- User must **not leave the TUI** to run the importer.
