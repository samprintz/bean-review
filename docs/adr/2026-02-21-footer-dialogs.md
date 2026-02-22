# Footer Dialogs Over Modal Dialogs

The application needs dialogs for:

- Account selector with fuzzy search
- Help menu displaying keybindings
- Confirm prompts (write/quit)

## Decision

Use footer dialogs that slide up from the bottom of the screen instead of centered modal dialogs.

## Rationale

- Keeps transaction list visible for context
- Consistent with vim/fzf-style interfaces
- Single-line confirm dialogs minimize disruption
- Scrollable footer for help menu when content exceeds screen height

## Consequences

- Input fields position at screen bottom (natural for CLI users)
- ESC/q consistently closes all footer dialogs
