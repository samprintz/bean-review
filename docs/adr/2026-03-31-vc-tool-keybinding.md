# Version Control Tool Keybinding

When reviewing and staging beancount transactions, users often want to open
a version control tool to inspect changes, commit staged files, or browse
ledger history — without leaving the review workflow.

## Decision

Add an `open_vc` action (default key: `V`) to both the Inbox Screen and the
Transaction List Screen.

The command to run is configured via `vc_cmd` in the `[general]` section of
the config file, following the same pattern as `import_cmd`: the key is inert
until configured, and pressing `V` without a configured command shows an error
hint to set `vc_cmd` in the config file.

The command is passed to the shell (`subprocess.call(..., shell=True)`) so that
environment variables like `$BEANCOUNT_LEDGER_DIR` are expanded at runtime.

The TUI is suspended via `app.suspend()` while the external tool runs, the same
mechanism used for `$EDITOR` invocations. The TUI resumes automatically when
the tool exits.

## Consequences

- Requires explicit configuration, consistent with `import_cmd`.
- Shell variable expansion allows commands like `tig -C $BEANCOUNT_LEDGER_DIR`.
- Available from both screens so users can check VC status at any point.
