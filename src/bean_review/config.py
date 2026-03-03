"""Configuration handling for beancount-reviewer."""

import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_CONFIG_PATH = Path("~/.config/beancount/bean-review.conf").expanduser()

DEFAULT_KEYBINDINGS = {
    "up": "k",
    "down": "j",
    "top": "g g",
    "bottom": "G",
    "half_page_down": "ctrl+d",
    "half_page_up": "ctrl+u",
    "select": "enter",
    "toggle_select": "space",
    "next_incomplete": "n",
    "prev_incomplete": "p",
    "filter_incomplete": "Z",
    "edit_category": "c",
    "toggle_complete": "u",
    "edit_external": "E",
    "edit_narration_append": "A",
    "edit_narration_insert": "I",
    "edit_narration_substitute": "S",
    "save": "w",
    "quit": "q",
    "invert_selection": "v",
    "help": "question_mark",
}


@dataclass
class Config:
    keybindings: dict[str, str] = field(default_factory=lambda: DEFAULT_KEYBINDINGS.copy())
    ledger_file: str | None = None

    def get_key(self, action: str) -> str:
        return self.keybindings.get(action, DEFAULT_KEYBINDINGS.get(action, ""))


def _resolve_path(path: str | None) -> str | None:
    """Resolve a path string, expanding user home and making absolute."""
    if not path:
        return None
    return Path(path).expanduser().resolve().as_posix()


def load_config(
    config_path: Path | str | None = None,
    ledger_file_override: str | None = None,
) -> Config:
    """Load configuration from file.

    Args:
        config_path: Path to config file. If None, uses default location.
        ledger_file_override: CLI override for ledger file path (highest priority).

    Returns:
        Config object with loaded or default settings.

    Ledger file resolution priority: CLI > config file > BEANCOUNT_FILE env var.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path).expanduser()

    config = Config()

    config_file_ledger: str | None = None

    if config_path.exists():
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if "general" in parser:
            config_file_ledger = parser["general"].get("ledger_file")

        if "keybindings" in parser:
            for action, key in parser["keybindings"].items():
                if action in DEFAULT_KEYBINDINGS:
                    config.keybindings[action] = key

    # Resolve ledger_file with priority: CLI > config file > env
    env_ledger = os.environ.get("BEANCOUNT_FILE")

    if ledger_file_override:
        config.ledger_file = _resolve_path(ledger_file_override)
    elif config_file_ledger:
        config.ledger_file = _resolve_path(config_file_ledger)
    elif env_ledger:
        config.ledger_file = _resolve_path(env_ledger)

    return config
