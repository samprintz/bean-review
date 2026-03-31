from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ..keymap import Keymap
from .keybinding_hints import KeybindingHints


class Footer(Widget):
    """Footer with keybinding hints and an optional right-side status slot."""

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

    Footer .footer-right {
        width: auto;
        height: 1;
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

    Footer .footer-status.hidden {
        display: none;
    }
    """

    state: reactive[str | None] = reactive(None)
    status: reactive[str | None] = reactive(None)

    # Default actions to show in footer (in order)
    FOOTER_ACTIONS = [
        "help",
        "edit_category",
        "select",
        "save",
        "append_and_archive",
        "quit",
    ]

    def __init__(
        self,
        keymap: Keymap,
        footer_actions: list[str] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._keymap = keymap
        self._footer_actions = (
            footer_actions if footer_actions is not None
            else self.FOOTER_ACTIONS
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield KeybindingHints(
                self._keymap,
                self._footer_actions,
                id="footer-hints",
            )
            with Horizontal(classes="footer-right"):
                state_class = (
                    "footer-state hidden"
                    if self.state is None
                    else "footer-state"
                )
                yield Static(
                    self.state or "",
                    id="footer-state",
                    classes=state_class,
                )
                status_class = (
                    "footer-status hidden"
                    if self.status is None
                    else "footer-status"
                )
                yield Static(
                    self.status or "",
                    id="footer-status",
                    classes=status_class,
                )

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

    def watch_status(self, new_status: str | None) -> None:
        """React to status text changes."""
        try:
            status_widget = self.query_one("#footer-status", Static)
            if new_status is None:
                status_widget.add_class("hidden")
                status_widget.update("")
            else:
                status_widget.remove_class("hidden")
                status_widget.update(new_status)
        except Exception:
            pass

    def update_keymap(self, keymap: Keymap) -> None:
        """Update the footer with a new keymap."""
        self._keymap = keymap
        try:
            self.query_one(
                "#footer-hints", KeybindingHints
            ).update_keymap(keymap)
        except Exception:
            pass
