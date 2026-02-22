"""Help footer widget for beancount-reviewer."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from keymap import Keymap


class HelpFooter(Widget):
    """Keybinding help display docked at bottom."""

    can_focus = True

    DEFAULT_CSS = """
    HelpFooter {
        dock: bottom;
        height: auto;
        max-height: 20;
        background: $surface;
        border-top: solid $primary;
    }

    HelpFooter #help-content {
        height: auto;
        padding: 0 1;
    }

    HelpFooter .help-row {
        height: 1;
        width: 100%;
        layout: horizontal;
    }

    HelpFooter .help-key {
        width: auto;
        height: 1;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }

    HelpFooter .help-desc {
        width: auto;
        height: 1;
        color: $text-muted;
        padding: 0 2 0 0;
    }

    HelpFooter #help-footer-line {
        height: 1;
        background: $primary;
        layout: horizontal;
    }

    HelpFooter .footer-key {
        width: auto;
        height: 1;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }

    HelpFooter .footer-desc {
        width: auto;
        height: 1;
        color: $text-muted;
        padding: 0 1;
    }
    """

    class Closed(Message):
        """Message sent when help footer is closed."""

        pass

    def __init__(
        self,
        keymap: Keymap,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._keymap = keymap

    def compose(self) -> ComposeResult:
        with Vertical(id="help-content"):
            for key, description in self._keymap.all_bindings():
                display_key = self._format_key(key)
                with Horizontal(classes="help-row"):
                    yield Static(display_key, classes="help-key")
                    yield Static(description, classes="help-desc")

        with Horizontal(id="help-footer-line"):
            yield Static("?", classes="footer-key")
            yield Static("close", classes="footer-desc")

    def _format_key(self, key: str) -> str:
        """Format a key for display."""
        key_map = {
            "question_mark": "?",
            "ctrl+d": "C-d",
            "ctrl+u": "C-u",
            "enter": "Enter",
            "space": "Space",
        }
        return key_map.get(key, key)

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape" or event.key == "question_mark" or event.key == "q":
            self.post_message(self.Closed())
            event.prevent_default()
            event.stop()
