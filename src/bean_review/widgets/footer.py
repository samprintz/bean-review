from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ..keymap import Keymap


class Footer(Widget):
    """Custom footer with keybindings, state, and completion status."""

    DEFAULT_CSS = """
    Footer {
        dock: bottom;
        height: 1;
        background: $primary;
    }

    Footer Horizontal {
        width: 100%;
        height: 1;
    }

    Footer .footer-left {
        width: 1fr;
        height: 1;
    }

    Footer .footer-right {
        width: auto;
        height: 1;
    }

    Footer .footer-key {
        width: auto;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }

    Footer .footer-description {
        width: auto;
        color: $text-muted;
        padding: 0 1;
    }

    Footer .footer-state {
        width: auto;
        background: $warning;
        color: $text;
        padding: 0 1;
    }

    Footer .footer-state.hidden {
        display: none;
    }

    Footer .footer-status {
        width: auto;
        color: $text-muted;
        padding: 0 1;
    }
    """

    state: reactive[str | None] = reactive(None)
    complete: reactive[int] = reactive(0)
    total: reactive[int] = reactive(0)

    # Actions to show in footer (in order)
    FOOTER_ACTIONS = ["help", "edit_category", "select", "save", "quit"]

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
        with Horizontal():
            with Horizontal(classes="footer-left"):
                # Build reverse mapping: action -> key
                action_to_key: dict[str, str] = {}
                for key, action_name in self._keymap.bindings.items():
                    if action_name not in action_to_key:
                        action_to_key[action_name] = key

                for action_name in self.FOOTER_ACTIONS:
                    if action_name in action_to_key:
                        key = action_to_key[action_name]
                        # Format key for display
                        display_key = self._format_key(key)
                        desc = self._keymap.actions[action_name].description
                        yield Static(display_key, classes="footer-key")
                        yield Static(desc, classes="footer-description")

            with Horizontal(classes="footer-right"):
                state_class = "footer-state hidden" if self.state is None else "footer-state"
                yield Static(self.state or "", id="footer-state", classes=state_class)
                yield Static(
                    f"{self.complete}/{self.total} complete",
                    id="footer-status",
                    classes="footer-status",
                )

    def _format_key(self, key: str) -> str:
        """Format a key for display in footer."""
        # Convert internal key names to display format
        key_map = {
            "question_mark": "?",
            "ctrl+d": "C-d",
            "ctrl+u": "C-u",
        }
        return key_map.get(key, key)

    def watch_state(self, new_state: str | None) -> None:
        """React to state changes."""
        try:
            state_widget = self.query_one("#footer-state", Static)
            if new_state is None:
                state_widget.add_class("hidden")
                state_widget.update("")
            else:
                state_widget.remove_class("hidden")
                state_widget.update(new_state)
        except Exception:
            pass

    def watch_complete(self, _: int) -> None:
        """React to complete count changes."""
        self._update_status()

    def watch_total(self, _: int) -> None:
        """React to total count changes."""
        self._update_status()

    def _update_status(self) -> None:
        """Update the status display."""
        try:
            status_widget = self.query_one("#footer-status", Static)
            status_widget.update(f"{self.complete}/{self.total} complete")
        except Exception:
            pass

    def update_keymap(self, keymap: Keymap) -> None:
        """Update the footer with a new keymap."""
        self._keymap = keymap
        self.refresh(recompose=True)


# Keep old name for compatibility during transition
KeybindingsFooter = Footer
