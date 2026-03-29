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
    "toggle_complete": "m",
    "edit_external": "E",
    "edit_narration_external": "e",
    "edit_narration_append": "A",
    "edit_narration_insert": "I",
    "edit_narration_substitute": "S",
    "predict_selected": "P",
    "predict_all_unconfirmed": "g P",
    "save": "w",
    "append_to_ledger": "W",
    "quit": "q",
    "invert_selection": "v",
    "unselect_all": "u v",
    "help": "question_mark",
    "import_active": "B",
    "import_all_pending": "g B",
    "view_inbox": "h",
}


@dataclass
class Config:
    keybindings: dict[str, str] = field(default_factory=lambda: DEFAULT_KEYBINDINGS.copy())
    ledger_file: str | None = None
    ai_host: str | None = None
    ai_port: int = 8080
    import_cmd: str | None = None
    import_all_cmd: str | None = None

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
    ai_host_override: str | None = None,
    ai_port_override: int | None = None,
) -> Config:
    """Load configuration from file.

    Args:
        config_path: Path to config file. If None, uses default location.
        ledger_file_override: CLI override for ledger file path (highest priority).
        ai_host_override: CLI override for AI service host.
        ai_port_override: CLI override for AI service port.

    Returns:
        Config object with loaded or default settings.

    Ledger file resolution priority: CLI > config file > BEANCOUNT_FILE env var.
    Import commands: import_cmd for single-file import;
    import_all_cmd for bulk import (falls back to import_cmd if not set).
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    else:
        config_path = Path(config_path).expanduser()

    config = Config()

    config_file_ledger: str | None = None
    config_file_import_cmd: str | None = None
    config_file_import_all_cmd: str | None = None

    if config_path.exists():
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if "general" in parser:
            config_file_ledger = parser["general"].get("ledger_file")
            config_file_import_cmd = parser["general"].get("import_cmd")
            config_file_import_all_cmd = parser["general"].get("import_all_cmd")

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

    config.import_cmd = config_file_import_cmd or None
    config.import_all_cmd = config_file_import_all_cmd \
            or config_file_import_cmd or None

    if ai_host_override:
        config.ai_host = ai_host_override
    if ai_port_override:
        config.ai_port = ai_port_override

    return config
