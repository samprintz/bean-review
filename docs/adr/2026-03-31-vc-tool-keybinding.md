# Version Control Tool Keybinding

When reviewing and staging beancount transactions, users often want to open
a version control tool to inspect changes, commit staged files, or browse
ledger history — without leaving the review workflow.

## Decision

Add an `open_vc` action (default key: `V`) to both the Inbox Screen and the
Transaction List Screen.

The command to run is configured via `vc_cmd` in the `[general]` section of
the config file. Unlike `import_cmd`, `vc_cmd` ships with a built-in default:

```
tig -C $BEANCOUNT_LEDGER_DIR
```

This follows the pattern of `$EDITOR` used for external editing: a sensible
default that works out of the box, overridable for those with different
preferences.

The command is passed to the shell (`subprocess.call(..., shell=True)`) so that
environment variables like `$BEANCOUNT_LEDGER_DIR` are expanded at runtime.

The TUI is suspended via `app.suspend()` while the external tool runs, the same
mechanism used for `$EDITOR` invocations. The TUI resumes automatically when
the tool exits.

## Consequences

- Works without any configuration (unlike `import_cmd`).
- Shell variable expansion makes the default command self-contained.
- Available from both screens so users can check VC status at any point.
