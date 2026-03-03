# beancount-reviewer

## Installation

As executable:

```bash
pipx install .
```

For development:

```bash
pyenv virtualenv bean-review
pyenv activate bean-review
pip install -e .
```

## Usage

Call with input file:

    bean-review <input_file>

Directly read from beangulp importer output:

    bean-review <(python import.py extract $BEANCOUNT_IMPORT_DIR)

## Configuration

- Default config: `~/.config/beancount/bean-review.conf`
- Override with `--config` CLI argument

### Keybindings

Keybindings configurable in config file.

### Main Ledger File Resolution

Priority (descending):
1. CLI: `--ledger-file`
2. Config: `[general]` → `ledger_file`
3. Environment: `BEANCOUNT_FILE`
