# bean-review Specification

## Project Overview

`bean-review` is a Python TUI application using `textual`
to review and edit beancount transactions.
The app reads transactions from an input file or a directory (inbox).
The transactions can be reviewed and edited
with bulk editing and AI features.
The result can be saved back to the source file
or appended to a main ledger file.

## Requirements

### Invocation

`bean-review` accepts a single positional argument:

- **File**: a `.beancount` file — opens the Transaction List Screen directly.
- **Directory**: an inbox directory — opens the Inbox Screen.

### Inbox Screen

The inbox screen is shown when `bean-review` is called with a directory argument.

The inbox is a directory
(with possible subdirectories,
including symlinked directories)
that contains import files (CSV, PDF, …)
alongside their `.beancount` counterparts produced by `bean-stage`.

- Each import file (non-`.beancount`) is one list entry.
- Nested files are listed by their path relative to the inbox root.
- Entries with a corresponding `<file>.beancount` are **reviewable** (displayed normally).
- Entries without a beancount file are **pending** (displayed dimmed).
- `enter` on a reviewable entry opens the Transaction List Screen for that file.
- `enter` on a pending entry shows a warning notification.
- `B` imports the focused file by running the configured import command
  with the file path as argument.
  If the file is already imported (reviewable),
  a confirm dialog asks before overwriting.
  If no import command is configured,
  - the confirm footer shows a hint to set `import_cmd` in the config file.
- `g B` imports all pending files by running the import command
  with the inbox directory as argument.
- After import the list is refreshed automatically.
- `F5` refreshes the inbox list.
- Import commands are configured in the `[general]` section of the config file:
  - `import_cmd`: used for single-file import (`B`) and as fallback for `g B`.
  - `import_all_cmd`: used for bulk import (`g B`)
  There is no default; the keys are inert until a command is configured.
- `V` opens a version control tool for the beancount ledger directory.
  - Configured via `version_control_cmd` in the `[general]` section of the config file.
  - There is no default; pressing `V` without configuration shows a hint.
  - The TUI is suspended while the tool runs; it resumes on exit.
  - The command is passed to the shell, so environment variables are expanded.
- `q` quits the application.
- The `InboxEntry` data class represents one entry: `import_file`, `beancount_file`
  (or `None`), and `inbox_root`.

When the Transaction List Screen is opened from the Inbox Screen:
- `h` and `esc` (when no footer dialog is active) return to the Inbox Screen.
- `w` saves to the `.beancount` file for that inbox entry.
- `q` quits the application.

### Transaction List Screen

- Display transactions in beancount format (header + posting lines)
- Bottom status bar shows "(k/n complete)" count
- Highlight incomplete transactions (missing `*` flag)
- `ENTER`/`E` opens transaction in `$EDITOR`
- `e` opens narration of focused/selected transaction(s) in `$EDITOR`
- `SPACE` selects/deselects focused transaction
- `u` toggles complete status (focused or all selected)
- `c` opens account selector (focused or all selected)
- `a`/`i`/`s` edits narration (append/insert/substitute mode)
- `P` predicts account for focused or selected transactions (requires `--ai-host`)
- `g P` predicts accounts for all unconfirmed transactions (requires `--ai-host`)
- `n`/`p` jumps to next/previous incomplete transaction
- `Z` filters to show only incomplete transactions
- `w` saves transactions to source file (with confirm);
  shows error if source is not a regular file (e.g. process substitution)
- `W` appends transactions to configured ledger file (with confirm)
  shows error of no ledger file configured
- `q` quits (with confirm)
- `V` opens the version control tool (see Inbox Screen for configuration)
- Editing preserves focus on current transaction

### Navigation

- vim-like keybindings for list navigation
- `j`/`k` moves down/up one item
- `gg`/`G` jumps to first/last item
- `C-d`/`C-u` scrolls half-page down/up
- Footer shows keybindings: `?`, `c`, `enter`, `w`, `W`, `q`

### Account Selector

- Fuzzy search over accounts from main ledger file
- Opens as footer dialog, input at bottom, results above
- Edits expense/income account (not asset)
- Close with `ESC` or `q`
- Shows hint if no ledger file configured

### Narration Editor

- Single-line text input footer dialog
- vim-like modes: `a` (append), `i` (insert), `s` (substitute)
- Applies to focused or all selected transactions
- Submit with `ENTER`, cancel with `ESC`

### Help Menu

- `?` toggles help from any screen
- Shows all keybindings with descriptions
- Respects configured keybinding overrides
- Shows one line per keybinding
- Opens as scrollable footer dialog
- Close with `?`, `q`, or `ESC`

### Confirm Dialog

- Single-line footer: message left, `y`/`n` right
- Close with `ESC` (cancels action)

## Architecture

```
src/
  screens/
  widgets/
  util.py
  config.py
  keymap.py
  models.py
```

Each screen and dialog is a separate class in a separate file.

## Modules

- Use `beancount` for parsing and handling transactions,
  e.g. `beancount.loader` or `beancount.parser.printer`.
- Use the types provided by `beancount` for transactions, postings, etc.,
  see `beancount.core.data`.
- Use `textual` as TUI module.
- Use `configparser` and `argparse` for argument and configuration file parsing.

## Architecture Design Decisions

See `docs/adr/` for design decisions and rationale.

## Transaction Format

Transactions are in Beancount format
(https://beancount.github.io/docs/beancount_language_syntax.html):

```
2002-02-20 * "Grocery store"
  Assets:Cash      -5.99 EUR
  Expenses:Food     5.99 EUR
```

A transaction is *complete* if it has the `*` between date and narration.

An example of an import file is in  `test.beancount`.
