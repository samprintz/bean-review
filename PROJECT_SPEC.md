# bean-review Specification

## Project Overview

`bean-review` is a Python TUI application using `textual`
to review beancount transactions.
The app reads transactions from an input file,
allows manual review/editing,
and appends reviewed transactions to the main ledger file.

## Requirements

### Transaction List Screen

- Display transactions in beancount format (header + posting lines)
- Bottom status bar shows "(k/n complete)" count
- Highlight incomplete transactions (missing `*` flag)
- `ENTER`/`E` opens transaction in `$EDITOR`
- `e` opens narration of focused/selected transaction(s) in `$EDITOR`
- `SPACE` selects/deselects focused transaction
- `u` toggles complete status (focused or all selected)
- `c` opens account selector (focused or all selected)
- `A`/`I`/`S` edits narration (append/insert/substitute mode)
- `P` predicts account for focused or selected transactions (requires `--ai-host`)
- `g P` predicts accounts for all unconfirmed transactions (requires `--ai-host`)
- `n`/`p` jumps to next/previous incomplete transaction
- `Z` filters to show only incomplete transactions
- `w` writes transactions (with confirm)
- `q` quits (with confirm)
- Editing preserves focus on current transaction

### Navigation

- vim-like keybindings for list navigation
- `j`/`k` moves down/up one item
- `gg`/`G` jumps to first/last item
- `C-d`/`C-u` scrolls half-page down/up
- Footer shows keybindings: `?`, `c`, `enter`, `w`, `q`

### Account Selector

- Fuzzy search over accounts from main ledger file
- Opens as footer dialog, input at bottom, results above
- Edits expense/income account (not asset)
- Close with `ESC` or `q`
- Shows hint if no ledger file configured

### Narration Editor

- Single-line text input footer dialog
- vim-like modes: `A` (append), `I` (insert), `S` (substitute)
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
beancount-reviewer.py    # Entry point
src/
  screens/
    transaction_list.py  # Main screen
  widgets/
    account_selector.py  # Fuzzy account search
    narration_editor.py  # Single-line text editor
    help_menu.py         # Keybinding display
    confirm_dialog.py    # y/n prompt
  config.py              # Configuration handling
  keybindings.py         # Keybinding definitions
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
