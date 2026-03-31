# Inbox Importer Execution

The inbox screen surfaces pending files (not yet transformed to `.beancount`).
Without an in-app trigger, the user must leave the TUI, run the importer manually,
and relaunch — breaking the review flow.

## Decision

Add an import action to the Inbox Screen:

Import the focused file (passes the file path to the import command).

The import command is run via subprocess in a background thread.
The list refreshes automatically on completion.
Triggering import on an already-imported file requires confirmation to prevent
accidental overwrites.

The action is configured via `import_cmd` in the `[general]` section.

## Consequences

- User must **not leave the TUI** to run the importer.
