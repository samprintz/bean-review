# Read Input From File Instead of Stdin

It would be nice to call `bean-review` with input from stdin
and append the result to the ledger file:

```bash
cat ingest.beancount | bean-review >> ledger.beancount
```

Unfortunately, this is not possible with `textual`
as when data is piped into the process,
the process’s standard input (stdin) is no longer the terminal,
it’s the pipe.
Most TUI frameworks depend on reading keystrokes directly from the terminal device,
not from a redirected pipe — and a pipe doesn’t support that.

As a workaround, the user can write the ingested transactions to a temporary file
and then pass that file as an argument to `bean-review`:

```bash
python import.py extract $BEANCOUNT_IMPORT_DIR > ingest.beancount
bean-review ingest.beancount >> ledger.beancount
```

or with process substitution:

```bash
bean-review <(python import.py extract $BEANCOUNT_IMPORT_DIR) >> ledger.beancount
```
