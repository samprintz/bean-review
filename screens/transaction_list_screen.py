"""Transaction list screen for beancount-reviewer."""

import os
import subprocess
import tempfile

from beancount.core.data import Transaction
from beancount.parser import parser, printer
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, ListItem, ListView

from config import Config
from keymap import Keymap
from models import load_accounts_from_ledger, ReviewFile, ReviewTransaction
from widgets import ConfirmFooter, EditTextFooter, Footer, FuzzySelectFooter, HelpFooter


class TransactionListItem(ListItem):
    """A list item representing a transaction."""

    def __init__(self, review_txn: ReviewTransaction, index: int) -> None:
        super().__init__()
        self.review_txn = review_txn
        self.index = index
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on transaction state."""
        if not self.review_txn.is_complete:
            self.add_class("incomplete")
        else:
            self.remove_class("incomplete")

        if self.review_txn.selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")

    def compose(self) -> ComposeResult:
        txn = self.review_txn.directive

        # Header: date "payee" "narration"
        header_parts = [str(txn.date)]
        if txn.payee:
            header_parts.append(f'"{txn.payee}"')
        if txn.narration:
            header_parts.append(f'"{txn.narration}"')
        header = " ".join(header_parts)

        # Posting lines
        posting_lines = []
        for posting in txn.postings:
            if posting.units:
                posting_lines.append(f"  {posting.account}  {posting.units}")
            else:
                posting_lines.append(f"  {posting.account}")

        full_text = header + "\n" + "\n".join(posting_lines)
        yield Label(full_text, classes="txn-content")


class TransactionListScreen(Screen):
    """Screen showing transactions for a specific file."""

    CSS = """
    TransactionListScreen {
        layout: vertical;
    }

    #transaction-list {
        height: 1fr;
    }

    TransactionListItem {
        height: auto;
        padding: 0 0 1 0;
    }

    .txn-content {
        height: auto;
    }

    .incomplete .txn-content {
        color: $error;
    }

    .selected {
        background: $secondary;
    }

    ListView > ListItem.--highlight {
        background: $accent;
    }
    """

    def __init__(
        self,
        review_file: ReviewFile,
        config: Config,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.review_file = review_file
        self.config = config
        self.keymap = Keymap.for_transaction_list(config)
        self._filter_incomplete = False
        self._active_footer: str | None = None  # "main", "confirm", "category", "help", "edit"
        self._confirm_action: str | None = None
        self._accounts: list[str] = []
        if config.ledger_file:
            self._accounts = load_accounts_from_ledger(config.ledger_file)

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="transaction-list")
        yield Footer(self.keymap, id="main-footer")

    def _update_footer_status(self) -> None:
        """Update the footer completion status."""
        try:
            footer = self.query_one("#main-footer", Footer)
            footer.complete = self.review_file.complete_count
            footer.total = self.review_file.total_count
        except Exception:
            pass

    def _update_footer_state(self) -> None:
        """Update the footer state indicator."""
        try:
            footer = self.query_one("#main-footer", Footer)
            if self._filter_incomplete:
                footer.state = "FILTERED"
            else:
                footer.state = None
        except Exception:
            pass

    def _restore_main_footer(self) -> None:
        """Restore the main footer, removing any temporary footer."""
        # Remove any temporary footers
        for footer_id in ["confirm-footer", "category-footer", "help-footer", "edit-footer"]:
            try:
                self.query_one(f"#{footer_id}").remove()
            except Exception:
                pass

        # Mount main footer if not present
        try:
            self.query_one("#main-footer", Footer)
        except Exception:
            self.mount(Footer(self.keymap, id="main-footer"))
            self._update_footer_status()
            self._update_footer_state()

        self._active_footer = "main"
        self._confirm_action = None
        list_view = self.query_one("#transaction-list", ListView)
        list_view.focus()

    def _restore_position_and_focus(self, current_idx: int | None) -> None:
        """Centralized method to restore position, focus, and highlight."""
        list_view = self.query_one("#transaction-list", ListView)
        if current_idx is not None:
            visible = self._get_visible_transactions()
            for list_idx, (real_idx, _) in enumerate(visible):
                if real_idx == current_idx:
                    list_view.index = list_idx
                    break
        list_view.focus()
        list_view.refresh()
        # Explicitly update highlight class
        children = list(list_view.children)
        if list_view.index is not None and 0 <= list_view.index < len(children):
            for i, item in enumerate(children):
                if isinstance(item, TransactionListItem):
                    if i == list_view.index:
                        item.add_class("suggestion-selected")
                    else:
                        item.remove_class("suggestion-selected")

    def on_mount(self) -> None:
        """Populate and focus the list view on mount."""
        self._active_footer = "main"
        self._rebuild_list()
        self._update_footer_status()
        current_idx = self._get_current_transaction_index()
        self._restore_position_and_focus(current_idx)

    def _rebuild_list(self) -> None:
        """Rebuild the transaction list."""
        list_view = self.query_one("#transaction-list", ListView)
        list_view.clear()

        transactions = self._get_visible_transactions()
        for i, txn in transactions:
            list_view.append(TransactionListItem(txn, i))

    def _get_visible_transactions(self) -> list[tuple[int, ReviewTransaction]]:
        """Get transactions to display based on filter state."""
        if self._filter_incomplete:
            return [
                (i, t)
                for i, t in enumerate(self.review_file.transactions)
                if not t.is_complete
            ]
        return list(enumerate(self.review_file.transactions))

    def _get_current_transaction_index(self) -> int | None:
        """Get the actual transaction index from current list position."""
        list_view = self.query_one("#transaction-list", ListView)
        if list_view.index is None:
            return None

        children = list(list_view.children)
        if 0 <= list_view.index < len(children):
            item = children[list_view.index]
            if isinstance(item, TransactionListItem):
                return item.index
        return None

    def _run_action(self, action: str) -> None:
        """Execute an action by name."""
        action_map = {
            "up": self._cursor_up,
            "down": self._cursor_down,
            "top": self._goto_top,
            "bottom": self._goto_bottom,
            "half_page_down": self._half_page_down,
            "half_page_up": self._half_page_up,
            "select": self._edit_inline,
            "toggle_select": self._toggle_select,
            "next_incomplete": self._next_incomplete,
            "prev_incomplete": self._prev_incomplete,
            "filter_incomplete": self._filter_incomplete_toggle,
            "edit_category": self._edit_category,
            "toggle_complete": self._toggle_complete,
            "edit_external": self._edit_external,
            "edit_narration_append": lambda: self._edit_narration("append"),
            "edit_narration_insert": lambda: self._edit_narration("insert"),
            "edit_narration_substitute": lambda: self._edit_narration("substitute"),
            "invert_selection": self._invert_selection,
            "save": self._save,
            "quit": self._quit_app,
            "help": self._show_help,
        }
        handler = action_map.get(action)
        if handler:
            handler()

    def _cursor_down(self) -> None:
        """Move cursor down."""
        list_view = self.query_one("#transaction-list", ListView)
        list_view.action_cursor_down()

    def _cursor_up(self) -> None:
        """Move cursor up."""
        list_view = self.query_one("#transaction-list", ListView)
        list_view.action_cursor_up()

    def _goto_top(self) -> None:
        """Go to top of list."""
        list_view = self.query_one("#transaction-list", ListView)
        list_view.index = 0

    def _goto_bottom(self) -> None:
        """Go to bottom of list."""
        list_view = self.query_one("#transaction-list", ListView)
        visible = self._get_visible_transactions()
        if visible:
            list_view.index = len(visible) - 1

    def _half_page_down(self) -> None:
        """Move cursor down by half page (vim-like C-d)."""
        list_view = self.query_one("#transaction-list", ListView)
        visible = self._get_visible_transactions()
        if not visible:
            return
        # Estimate items per page: ~4 lines per transaction (header + 2 postings + padding)
        items_per_page = max(1, list_view.size.height // 4)
        half_page = max(1, items_per_page // 2)
        current = list_view.index or 0
        new_index = min(current + half_page, len(visible) - 1)
        list_view.index = new_index

    def _half_page_up(self) -> None:
        """Move cursor up by half page (vim-like C-u)."""
        list_view = self.query_one("#transaction-list", ListView)
        visible = self._get_visible_transactions()
        if not visible:
            return
        # Estimate items per page: ~4 lines per transaction (header + 2 postings + padding)
        items_per_page = max(1, list_view.size.height // 4)
        half_page = max(1, items_per_page // 2)
        current = list_view.index or 0
        new_index = max(current - half_page, 0)
        list_view.index = new_index

    def _toggle_select(self) -> None:
        """Toggle selection of current transaction."""
        idx = self._get_current_transaction_index()
        if idx is not None:
            txn = self.review_file.transactions[idx]
            txn.selected = not txn.selected
            self._rebuild_list()
            self._restore_position_and_focus(idx)

    def _next_incomplete(self) -> None:
        """Jump to next incomplete transaction."""
        current_idx = self._get_current_transaction_index()
        if current_idx is None:
            current_idx = -1

        visible = self._get_visible_transactions()
        for list_idx, (real_idx, txn) in enumerate(visible):
            if real_idx > current_idx and not txn.is_complete:
                list_view = self.query_one("#transaction-list", ListView)
                list_view.index = list_idx
                return

    def _prev_incomplete(self) -> None:
        """Jump to previous incomplete transaction."""
        current_idx = self._get_current_transaction_index()
        if current_idx is None:
            current_idx = len(self.review_file.transactions)

        visible = self._get_visible_transactions()
        for list_idx in range(len(visible) - 1, -1, -1):
            real_idx, txn = visible[list_idx]
            if real_idx < current_idx and not txn.is_complete:
                list_view = self.query_one("#transaction-list", ListView)
                list_view.index = list_idx
                return

    def _filter_incomplete_toggle(self) -> None:
        """Toggle filter to show only incomplete transactions."""
        self._filter_incomplete = not self._filter_incomplete
        self._update_footer_state()
        self._rebuild_list()

    def _toggle_complete(self) -> None:
        """Toggle complete/incomplete flag for selected or current transaction."""
        current_idx = self._get_current_transaction_index()

        # Get selected transactions or current transaction
        selected_indices = [
            i for i, t in enumerate(self.review_file.transactions) if t.selected
        ]

        if not selected_indices:
            if current_idx is not None:
                selected_indices = [current_idx]

        for idx in selected_indices:
            txn = self.review_file.transactions[idx]
            self.review_file.transactions[idx] = txn.toggle_complete()

        self._rebuild_list()
        self._update_footer_status()

        # Restore position and focus
        list_view = self.query_one("#transaction-list", ListView)
        if current_idx is not None:
            visible = self._get_visible_transactions()
            for list_idx, (real_idx, _) in enumerate(visible):
                if real_idx == current_idx:
                    list_view.index = list_idx
                    break
        list_view.focus()
        list_view.refresh()

    def _edit_category(self) -> None:
        """Show footer to edit category/account."""
        # Remove main footer and mount category footer
        try:
            self.query_one("#main-footer").remove()
        except Exception:
            pass

        self._active_footer = "category"
        footer = FuzzySelectFooter(options=self._accounts, id="category-footer")
        self.mount(footer)

    def _apply_category(self, new_account: str) -> None:
        """Apply new account to selected or current transactions."""
        current_idx = self._get_current_transaction_index()

        selected_indices = [
            i for i, t in enumerate(self.review_file.transactions) if t.selected
        ]

        if not selected_indices:
            if current_idx is not None:
                selected_indices = [current_idx]

        for idx in selected_indices:
            txn = self.review_file.transactions[idx]
            directive = txn.directive

            # Find and replace non-asset account
            new_postings = []
            for posting in directive.postings:
                if posting.account.startswith("Assets:") or posting.account.startswith(
                    "Liabilities:"
                ):
                    new_postings.append(posting)
                else:
                    new_postings.append(posting._replace(account=new_account))

            new_directive = directive._replace(postings=new_postings)
            self.review_file.transactions[idx] = txn.with_directive(new_directive)

        self._rebuild_list()
        self._restore_position_and_focus(current_idx)

    def _edit_narration(self, mode: str) -> None:
        """Show footer to edit narration.

        Args:
            mode: "append" (cursor at end), "insert" (cursor at start),
                  or "substitute" (start empty)
        """
        current_idx = self._get_current_transaction_index()
        if current_idx is None:
            return

        txn = self.review_file.transactions[current_idx]
        current_narration = txn.directive.narration or ""

        if mode == "substitute":
            initial_value = ""
            cursor_position = 0
        elif mode == "insert":
            initial_value = current_narration
            cursor_position = 0
        else:  # append
            initial_value = current_narration
            cursor_position = len(current_narration)

        # Remove main footer and mount edit footer
        try:
            self.query_one("#main-footer").remove()
        except Exception:
            pass

        self._active_footer = "edit"
        footer = EditTextFooter(
            initial_value=initial_value,
            cursor_position=cursor_position,
            placeholder="Edit narration (Escape to cancel)",
            id="edit-footer",
        )
        self.mount(footer)

    def _apply_narration(self, new_narration: str) -> None:
        """Apply new narration to selected or current transactions."""
        current_idx = self._get_current_transaction_index()

        selected_indices = [
            i for i, t in enumerate(self.review_file.transactions) if t.selected
        ]

        if not selected_indices:
            if current_idx is not None:
                selected_indices = [current_idx]

        for idx in selected_indices:
            txn = self.review_file.transactions[idx]
            directive = txn.directive
            new_directive = directive._replace(narration=new_narration)
            self.review_file.transactions[idx] = txn.with_directive(new_directive)

        self._rebuild_list()
        self._restore_position_and_focus(current_idx)

    def on_edit_text_footer_submitted(self, event: EditTextFooter.Submitted) -> None:
        """Handle narration edit submission."""
        self._apply_narration(event.value)
        self._restore_main_footer()

    def on_edit_text_footer_cancelled(self, event: EditTextFooter.Cancelled) -> None:
        """Handle narration edit cancellation."""
        self._restore_main_footer()

    def on_fuzzy_select_footer_selected(
        self, event: FuzzySelectFooter.Selected
    ) -> None:
        """Handle category selection from FuzzySelectFooter."""
        self._apply_category(event.value)
        self._restore_main_footer()

    def on_fuzzy_select_footer_cancelled(
        self, event: FuzzySelectFooter.Cancelled
    ) -> None:
        """Handle category selection cancellation."""
        self._restore_main_footer()

    def on_confirm_footer_confirmed(self, event: ConfirmFooter.Confirmed) -> None:
        """Handle confirmation from ConfirmFooter."""
        action = self._confirm_action
        self._restore_main_footer()
        if action == "save":
            self.app.save_and_exit()
        elif action == "quit":
            self.app.exit()

    def on_confirm_footer_cancelled(self, event: ConfirmFooter.Cancelled) -> None:
        """Handle confirmation cancellation."""
        self._restore_main_footer()

    def on_help_footer_closed(self, event: HelpFooter.Closed) -> None:
        """Handle help footer closed."""
        self._restore_main_footer()

    def on_key(self, event) -> None:
        """Handle key events."""
        # If a special footer is active, let it handle keys
        if self._active_footer in ("confirm", "category", "help", "edit"):
            return

        action = self.keymap.resolve(event.key)
        if action:
            self._run_action(action)
            event.prevent_default()
            event.stop()
        elif not self.keymap.has_pending():
            # Unknown key and not waiting for multi-key sequence
            self.keymap.reset_pending()

    def _edit_external(self) -> None:
        """Edit selected transaction(s) in external editor."""
        current_idx = self._get_current_transaction_index()

        selected_indices = [
            i for i, t in enumerate(self.review_file.transactions) if t.selected
        ]

        if not selected_indices:
            if current_idx is not None:
                selected_indices = [current_idx]

        if not selected_indices:
            return

        editor = os.environ.get("EDITOR", "vi")

        # Format transactions for editing
        txn_texts = []
        for idx in selected_indices:
            txn = self.review_file.transactions[idx].directive
            txn_texts.append(printer.format_entry(txn))

        content = "\n".join(txn_texts)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".beancount", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Suspend the app and run editor
            with self.app.suspend():
                subprocess.call([editor, temp_path])

            # Re-parse edited content
            with open(temp_path) as f:
                edited_content = f.read()

            entries, errors, _ = parser.parse_string(edited_content)
            edited_txns = [e for e in entries if isinstance(e, Transaction)]

            # Update transactions (match by index order)
            for i, idx in enumerate(selected_indices):
                if i < len(edited_txns):
                    old_txn = self.review_file.transactions[idx]
                    self.review_file.transactions[idx] = old_txn.with_directive(
                        edited_txns[i]
                    )

            self._rebuild_list()
            self._update_footer_status()
            self._restore_position_and_focus(current_idx)
        finally:
            os.unlink(temp_path)

    def _edit_inline(self) -> None:
        """Edit current transaction inline (opens external editor for now)."""
        self._edit_external()

    def _invert_selection(self) -> None:
        """Invert selection of all visible transactions."""
        visible = self._get_visible_transactions()
        for idx, _ in visible:
            txn = self.review_file.transactions[idx]
            txn.selected = not txn.selected
        self._rebuild_list()

    def _save(self) -> None:
        """Show save confirmation footer."""
        self._show_confirm("Save and exit?", "save")

    def _quit_app(self) -> None:
        """Show quit confirmation footer."""
        self._show_confirm("Quit without saving?", "quit")

    def _show_confirm(self, message: str, action: str) -> None:
        """Show confirmation footer."""
        # Remove main footer and mount confirm footer
        try:
            self.query_one("#main-footer").remove()
        except Exception:
            pass

        self._active_footer = "confirm"
        self._confirm_action = action
        footer = ConfirmFooter(message=message, id="confirm-footer")
        self.mount(footer)
        footer.focus()

    def _show_help(self) -> None:
        """Show the help footer."""
        # Remove main footer and mount help footer
        try:
            self.query_one("#main-footer").remove()
        except Exception:
            pass

        self._active_footer = "help"
        footer = HelpFooter(self.keymap, id="help-footer")
        self.mount(footer)
        footer.focus()
