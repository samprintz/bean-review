# Write to Ledger File Instead of Stdout

It would be convenient to write reviewed transactions to stdout
and redirect output to the ledger file:

```bash
bean-review ingest.beancount >> ledger.beancount
```

Unfortunately, this is not possible with `textual`.
When stdout is redirected to a file (`>` or `>>`),
the process's standard output is no longer connected to the terminal.
Most TUI frameworks depend on:

- stdout being attached to a TTY (terminal)
- Terminal size being queried via `ioctl()` on the TTY
- Direct control of the screen buffer

When stdout is redirected:

- `sys.stdout.isatty()` returns `False`
- Terminal size detection fails or falls back to defaults (often 80x24)
- The TUI cannot properly render

As a solution, the application writes directly to the ledger file
using the `--ledger-file` argument or the `BEANCOUNT_FILE` environment variable:

```bash
bean-review ingest.beancount --ledger-file ledger.beancount
```

This keeps stdout connected to the terminal for the TUI
while still appending transactions to the correct file.
