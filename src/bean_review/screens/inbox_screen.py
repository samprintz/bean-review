"""Inbox screen: lists import files in an inbox directory."""

import shlex
import subprocess

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, ListItem, ListView, Static

from ..config import Config
from ..keymap import Keymap
from ..models import InboxEntry
from ..util import create_review_file, parse_file, scan_inbox
from ..widgets import ConfirmFooter, MessageFooter


class InboxListItem(ListItem):
    """A list item representing one inbox entry (import file + optional beancount file)."""

    def __init__(self, entry: InboxEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        classes = "inbox-entry-reviewable" if self.entry.is_reviewable else "inbox-entry-pending"
        yield Label(self.entry.display_name, classes=classes)


class InboxScreen(Screen):
    """Screen showing the inbox directory contents."""

    CSS = """
    InboxScreen {
        layout: vertical;
    }

    #inbox-list {
        height: 1fr;
    }

    InboxListItem {
        height: 1;
    }

    .inbox-entry-pending {
        color: $text-muted;
    }

    #inbox-footer {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, inbox_dir: str, config: Config) -> None:
        super().__init__()
        self._inbox_dir = inbox_dir
        self._config = config
        self._keymap = Keymap.for_inbox(config)
        self._entries: list[InboxEntry] = []
        self._active_footer: str = "main"
        self._pending_import_entry: InboxEntry | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="inbox-list")
        yield Static("enter open  B import  g B import all  F5 refresh  q quit", id="inbox-footer")

    async def on_mount(self) -> None:
        await self._reload()

    async def _reload(self) -> None:
        """Reload inbox entries from disk and repopulate the list."""
        list_view = self.query_one("#inbox-list", ListView)
        previous_index = list_view.index or 0
        self._entries = scan_inbox(self._inbox_dir)
        await list_view.clear()
        await list_view.extend(
            [InboxListItem(entry) for entry in self._entries]
        )
        if self._entries:
            list_view.index = min(previous_index, len(self._entries) - 1)
        list_view.focus()

    def _restore_main_footer(self) -> None:
        for footer_id in ["confirm-footer", "message-footer"]:
            try:
                self.query_one(f"#{footer_id}").remove()
            except Exception:
                pass
        self._active_footer = "main"
        self._pending_import_entry = None
        self.query_one("#inbox-list", ListView).focus()

    def on_confirm_footer_confirmed(self, event: ConfirmFooter.Confirmed) -> None:
        entry = self._pending_import_entry
        self._restore_main_footer()
        if entry is not None:
            self._run_import_worker(entry.import_file)

    def on_confirm_footer_cancelled(self, event: ConfirmFooter.Cancelled) -> None:
        self._restore_main_footer()

    def on_message_footer_dismissed(
        self, event: MessageFooter.Dismissed
    ) -> None:
        self._restore_main_footer()

    def _show_confirm(self, message: str, entry: InboxEntry) -> None:
        self._active_footer = "confirm"
        self._pending_import_entry = entry
        self._mount_confirm_footer(message)

    def _show_error(self, message: str) -> None:
        self._active_footer = "message"
        self._pending_import_entry = None
        try:
            self.query_one("#inbox-footer").remove()
        except Exception:
            pass
        footer = MessageFooter(message=message, id="message-footer")
        self.mount(footer)
        footer.focus()

    def _mount_confirm_footer(self, message: str) -> None:
        try:
            self.query_one("#inbox-footer").remove()
        except Exception:
            pass
        footer = ConfirmFooter(message=message, id="confirm-footer")
        self.mount(footer)
        footer.focus()

    def _import_active(self) -> None:
        """Import the currently focused file."""
        if not self._config.import_cmd:
            self._show_error(
                "No import command configured. Set import_cmd in [general] in the config file."
            )
            return
        list_view = self.query_one("#inbox-list", ListView)
        idx = list_view.index
        if idx is None or idx >= len(self._entries):
            return
        entry = self._entries[idx]
        if entry.is_reviewable:
            self._show_confirm("Already imported. Overwrite?", entry)
            return
        self._run_import_worker(entry.import_file)

    def _import_all_pending(self) -> None:
        """Import all pending files by passing the inbox directory."""
        if not self._config.import_all_cmd:
            self._show_error(
                "No import command configured. Set import_all_cmd in [general] in the config file."
            )
            return
        self._run_import_worker(self._inbox_dir)

    def _run_import_worker(self, target: str) -> None:
        self.run_worker(
            lambda: self._run_import(target),
            thread=True,
            name="import",
        )

    def _run_import(self, target: str) -> None:
        """Run the import command against target; reload on completion."""
        cmd = shlex.split(self._config.import_all_cmd) + [target]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            self.app.call_from_thread(
                self.notify,
                f"Import failed (exit {result.returncode}).",
                severity="error",
            )
        else:
            self.app.call_from_thread(self.notify, "Import complete.")
        self.app.call_from_thread(self._reload)

    def _open_version_control(self) -> None:
        """Open the version control tool for the beancount ledger directory."""
        if not self._config.version_control_cmd:
            self._show_error(
                "No version control command configured."
                " Set version_control_cmd in [general] in the config file."
            )
            return
        with self.app.suspend():
            subprocess.call(self._config.version_control_cmd, shell=True)

    def _open_selected(self) -> None:
        """Open the transaction screen for the currently selected inbox entry."""
        list_view = self.query_one("#inbox-list", ListView)
        idx = list_view.index
        if idx is None or idx >= len(self._entries):
            return
        entry = self._entries[idx]
        if not entry.is_reviewable:
            self.notify("No beancount file for this entry yet.", severity="warning")
            return
        transactions = parse_file(entry.beancount_file)
        if not transactions:
            self.notify("No transactions found.", severity="warning")
            return
        review_file = create_review_file(transactions, entry.beancount_file)

        # Import here to avoid circular import at module level
        from .transaction_list_screen import TransactionListScreen
        self.app.push_screen(TransactionListScreen(
            review_file,
            self._config,
            source_file=entry.beancount_file,
            back_to_inbox=True,
        ))

    def on_key(self, event) -> None:
        if self._active_footer in ("confirm", "message"):
            return

        action = self._keymap.resolve(event.key)
        if action == "up":
            self.query_one("#inbox-list", ListView).action_cursor_up()
            event.prevent_default()
            event.stop()
        elif action == "down":
            self.query_one("#inbox-list", ListView).action_cursor_down()
            event.prevent_default()
            event.stop()
        elif action == "select":
            self._open_selected()
            event.prevent_default()
            event.stop()
        elif action == "import_active":
            self._import_active()
            event.prevent_default()
            event.stop()
        elif action == "import_all_pending":
            self._import_all_pending()
            event.prevent_default()
            event.stop()
        elif action == "refresh_inbox":
            self.run_worker(self._reload(), name="reload")
            event.prevent_default()
            event.stop()
        elif action == "open_version_control":
            self._open_version_control()
            event.prevent_default()
            event.stop()
        elif action == "quit":
            self.app.exit()
            event.prevent_default()
            event.stop()
