from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class MessageFooter(Widget):
    """Single-line message footer docked at bottom; dismissed with any key."""

    can_focus = True

    DEFAULT_CSS = """
    MessageFooter {
        dock: bottom;
        height: 1;
        background: $error;
        layout: horizontal;
    }

    MessageFooter .message-text {
        width: 1fr;
        height: 1;
        padding: 0 1;
        color: $text;
    }

    MessageFooter .message-key {
        width: auto;
        height: 1;
        background: $secondary;
        padding: 0 1;
    }

    MessageFooter .message-action {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $text;
    }
    """

    message: reactive[str] = reactive("")

    class Dismissed(Message):
        """Message sent when user dismisses the footer."""

        pass

    def __init__(
        self,
        message: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(self.message, classes="message-text")
        yield Static("Esc", classes="message-key")
        yield Static("dismiss", classes="message-action")

    def watch_message(self, new_message: str) -> None:
        """React to message changes."""
        try:
            msg_widget = self.query_one(".message-text", Static)
            msg_widget.update(new_message)
        except Exception:
            pass

    def on_key(self, event) -> None:
        """Dismiss on any key."""
        self.post_message(self.Dismissed())
        event.prevent_default()
        event.stop()
