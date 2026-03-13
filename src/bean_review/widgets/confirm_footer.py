from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class ConfirmFooter(Widget):
    """Single-line confirmation dialog docked at bottom."""

    can_focus = True

    DEFAULT_CSS = """
    ConfirmFooter {
        dock: bottom;
        height: 1;
        background: $error;
        layout: horizontal;
    }

    ConfirmFooter .confirm-message {
        width: 1fr;
        height: 1;
        padding: 0 1;
        color: $text;
    }

    ConfirmFooter .confirm-key {
        width: auto;
        height: 1;
        background: $secondary;
        padding: 0 1;
    }

    ConfirmFooter .confirm-action {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    """

    message: reactive[str] = reactive("")

    class Confirmed(Message):
        """Message sent when user confirms."""

        pass

    class Cancelled(Message):
        """Message sent when user cancels."""

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
        yield Static(self.message, classes="confirm-message")
        yield Static("y", classes="confirm-key")
        yield Static("confirm", classes="confirm-action")
        yield Static("n", classes="confirm-key")
        yield Static("cancel", classes="confirm-action")

    def watch_message(self, new_message: str) -> None:
        """React to message changes."""
        try:
            msg_widget = self.query_one(".confirm-message", Static)
            msg_widget.update(new_message)
        except Exception:
            pass

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "y":
            self.post_message(self.Confirmed())
            event.prevent_default()
            event.stop()
        elif event.key == "n" or event.key == "escape":
            self.post_message(self.Cancelled())
            event.prevent_default()
            event.stop()
