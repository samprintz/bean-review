"""Keymap and action registry for configurable keybindings."""

from dataclasses import dataclass, field

from .config import Config


@dataclass
class Action:
    """An action that can be triggered by a keybinding."""

    name: str
    description: str


# Action definitions for transaction list screen
TRANSACTION_LIST_ACTIONS = {
    "up": Action("up", "Up"),
    "down": Action("down", "Down"),
    "top": Action("top", "Top"),
    "bottom": Action("bottom", "Bottom"),
    "half_page_down": Action("half_page_down", "Half page down"),
    "half_page_up": Action("half_page_up", "Half page up"),
    "select": Action("select", "Edit transaction"),
    "toggle_select": Action("toggle_select", "Select"),
    "next_incomplete": Action("next_incomplete", "Next incomplete"),
    "prev_incomplete": Action("prev_incomplete", "Previous incomplete"),
    "filter_incomplete": Action("filter_incomplete", "Filter incomplete"),
    "edit_category": Action("edit_category", "Edit category"),
    "toggle_complete": Action("toggle_complete", "Toggle complete"),
    "edit_external": Action("edit_external", "Edit in external editor"),
    "edit_narration_external": Action("edit_narration_external", "Edit narration in external editor"),
    "edit_narration_append": Action("edit_narration_append", "Edit narration (append)"),
    "edit_narration_insert": Action("edit_narration_insert", "Edit narration (insert)"),
    "edit_narration_substitute": Action("edit_narration_substitute", "Edit narration (clear)"),
    "invert_selection": Action("invert_selection", "Invert selection"),
    "unselect_all": Action("unselect_all", "Unselect all"),
    "save": Action("save", "Save"),
    "append_to_ledger": Action("append_to_ledger", "Append to ledger"),
    "quit": Action("quit", "Quit"),
    "help": Action("help", "Help"),
    "predict_selected": Action("predict_selected", "Predict account(s)"),
    "predict_all_unconfirmed": Action("predict_all_unconfirmed", "Predict all unconfirmed"),
    "view_inbox": Action("view_inbox", "View inbox"),
    "open_version_control": Action("open_version_control", "Open version control"),
}


INBOX_ACTIONS = {
    "up": Action("up", "Up"),
    "down": Action("down", "Down"),
    "select": Action("select", "Open"),
    "import_active": Action("import_active", "Import file"),
    "import_all_pending": Action("import_all_pending", "Import all pending"),
    "refresh_inbox": Action("refresh_inbox", "Refresh"),
    "open_version_control": Action("open_version_control", "Open version control"),
    "quit": Action("quit", "Quit"),
    "help": Action("help", "Help"),
}


@dataclass
class Keymap:
    """Maps keys to actions with support for multi-key sequences."""

    bindings: dict[str, str] = field(default_factory=dict)
    actions: dict[str, Action] = field(default_factory=dict)
    _pending_key: str | None = field(default=None, init=False)

    @classmethod
    def for_transaction_list(cls, config: Config) -> "Keymap":
        """Create keymap for transaction list screen."""
        bindings = {
            config.get_key("up"): "up",
            config.get_key("down"): "down",
            config.get_key("top"): "top",
            config.get_key("bottom"): "bottom",
            config.get_key("half_page_down"): "half_page_down",
            config.get_key("half_page_up"): "half_page_up",
            config.get_key("select"): "select",
            config.get_key("toggle_select"): "toggle_select",
            config.get_key("next_incomplete"): "next_incomplete",
            config.get_key("prev_incomplete"): "prev_incomplete",
            config.get_key("filter_incomplete"): "filter_incomplete",
            config.get_key("edit_category"): "edit_category",
            config.get_key("toggle_complete"): "toggle_complete",
            config.get_key("edit_external"): "edit_external",
            config.get_key("edit_narration_external"): "edit_narration_external",
            config.get_key("edit_narration_append"): "edit_narration_append",
            config.get_key("edit_narration_insert"): "edit_narration_insert",
            config.get_key("edit_narration_substitute"): "edit_narration_substitute",
            config.get_key("invert_selection"): "invert_selection",
            config.get_key("unselect_all"): "unselect_all",
            config.get_key("save"): "save",
            config.get_key("append_to_ledger"): "append_to_ledger",
            config.get_key("quit"): "quit",
            config.get_key("help"): "help",
            config.get_key("predict_selected"): "predict_selected",
            config.get_key("predict_all_unconfirmed"): "predict_all_unconfirmed",
            config.get_key("view_inbox"): "view_inbox",
            config.get_key("open_version_control"): "open_version_control",
        }
        return cls(bindings=bindings, actions=TRANSACTION_LIST_ACTIONS)

    @classmethod
    def for_inbox(cls, config: Config) -> "Keymap":
        """Create keymap for inbox screen."""
        bindings = {
            config.get_key("up"): "up",
            config.get_key("down"): "down",
            config.get_key("select"): "select",
            config.get_key("import_active"): "import_active",
            config.get_key("import_all_pending"): "import_all_pending",
            config.get_key("refresh_inbox"): "refresh_inbox",
            config.get_key("open_version_control"): "open_version_control",
            config.get_key("quit"): "quit",
            config.get_key("help"): "help",
        }
        return cls(bindings=bindings, actions=INBOX_ACTIONS)

    def resolve(self, key: str) -> str | None:
        """Resolve a key press to an action name.

        Handles multi-key sequences like "g g" by tracking pending keys.
        Multi-key prefixes take priority over single-key matches so that e.g.
        "u v" (unselect_all) is reachable even though "u" is also bound.
        Returns the action name if resolved, None if waiting for more keys
        or no match.
        """
        if self._pending_key:
            # Try to complete a multi-key sequence
            sequence = f"{self._pending_key} {key}"
            self._pending_key = None
            if sequence in self.bindings:
                return self.bindings[sequence]
            # Sequence didn't match; try the new key as a prefix, then exact
            for binding_key in self.bindings:
                if " " in binding_key and binding_key.startswith(f"{key} "):
                    self._pending_key = key
                    return None
            if key in self.bindings:
                return self.bindings[key]
            return None

        # Check for multi-key prefix BEFORE exact single-key match so that a
        # key bound both alone and as a sequence prefix waits for the next key.
        for binding_key in self.bindings:
            if " " in binding_key and binding_key.startswith(f"{key} "):
                self._pending_key = key
                return None

        # Check for exact single-key match
        if key in self.bindings:
            return self.bindings[key]

        return None

    def reset_pending(self) -> None:
        """Reset any pending multi-key sequence."""
        self._pending_key = None

    def has_pending(self) -> bool:
        """Check if there's a pending multi-key sequence."""
        return self._pending_key is not None

    def all_bindings(self) -> list[tuple[str, str]]:
        """Get all keybindings: (key, description) pairs."""
        items = []
        # Build reverse mapping: action -> key
        action_to_key: dict[str, str] = {}
        for key, action_name in self.bindings.items():
            if action_name not in action_to_key:
                action_to_key[action_name] = key

        for action_name, action in self.actions.items():
            if action_name in action_to_key:
                key = action_to_key[action_name]
                items.append((key, action.description))

        return items
