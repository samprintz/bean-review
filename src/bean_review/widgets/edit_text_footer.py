from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input


class EditTextFooter(Widget):
    """Single-line text editing footer with vim-like cursor positioning."""

    DEFAULT_CSS = """
    EditTextFooter {
        dock: bottom;
        height: auto;
        background: $surface;
        border-top: solid $primary;
    }

    EditTextFooter #edit-input {
        height: 1;
        border: none;
        background: $surface;
        padding: 0 1;
    }

    EditTextFooter #edit-input:focus {
        border: none;
    }
    """

    class Submitted(Message):
        """Message sent when user submits the edited text."""

        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    class Cancelled(Message):
        """Message sent when user cancels editing."""

        pass

    def __init__(
        self,
        initial_value: str = "",
        cursor_position: int | None = None,
        placeholder: str = "Esc to cancel",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._initial_value = initial_value
        self._cursor_position = cursor_position
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Input(
            value=self._initial_value,
            placeholder=self._placeholder,
            select_on_focus=False,
            id="edit-input",
        )

    def on_mount(self) -> None:
        """Initialize input and set cursor position."""
        input_widget = self.query_one("#edit-input", Input)
        if self._cursor_position is not None:
            input_widget.cursor_position = self._cursor_position
        else:
            input_widget.cursor_position = len(self._initial_value)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "edit-input":
            self.post_message(self.Submitted(event.value))
            event.prevent_default()
            event.stop()

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.post_message(self.Cancelled())
            event.prevent_default()
            event.stop()
