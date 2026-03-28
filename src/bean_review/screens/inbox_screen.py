"""Inbox screen: lists import files in an inbox directory."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Label, ListItem, ListView, Static

from ..util import create_review_file, parse_file, scan_inbox
from ..config import Config
from ..keymap import Keymap
from ..models import InboxEntry


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

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="inbox-list")
        yield Static("enter open  q quit", id="inbox-footer")

    def on_mount(self) -> None:
        self._reload()

    def _reload(self) -> None:
        """Reload inbox entries from disk and repopulate the list."""
        self._entries = scan_inbox(self._inbox_dir)
        list_view = self.query_one("#inbox-list", ListView)
        list_view.clear()
        for entry in self._entries:
            list_view.append(InboxListItem(entry))
        if self._entries:
            list_view.index = 0
        list_view.focus()

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
        elif action == "quit":
            self.app.exit()
            event.prevent_default()
            event.stop()
