from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static

from ..keymap import Keymap


class KeybindingHints(Widget):
    """Displays key-badge / description pairs for a set of keymap actions."""

    DEFAULT_CSS = """
    KeybindingHints {
        width: 1fr;
        height: 1;
    }

    KeybindingHints .footer-key {
        width: auto;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }

    KeybindingHints .footer-description {
        width: auto;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        keymap: Keymap,
        actions: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._keymap = keymap
        self._actions = actions

    def compose(self) -> ComposeResult:
        with Horizontal():
            action_to_key: dict[str, str] = {}
            for key, action_name in self._keymap.bindings.items():
                if action_name not in action_to_key:
                    action_to_key[action_name] = key

            for action_name in self._actions:
                if action_name in action_to_key:
                    key = action_to_key[action_name]
                    display_key = self._format_key(key)
                    desc = self._keymap.actions[action_name].description
                    yield Static(display_key, classes="footer-key")
                    yield Static(desc, classes="footer-description")

    @staticmethod
    def _format_key(key: str) -> str:
        """Format a key name for display."""
        key_map = {
            "question_mark": "?",
            "ctrl+d": "C-d",
            "ctrl+u": "C-u",
        }
        return key_map.get(key, key)

    def update_keymap(self, keymap: Keymap) -> None:
        """Update the displayed keymap."""
        self._keymap = keymap
        self.refresh(recompose=True)
