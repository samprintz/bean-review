# bean-review

`bean-review` is a Python TUI application using `textual`
to review and edit beancount transactions.

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

Call with inbox directory to review all staged files:

    bean-review <inbox_dir>

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

### Import Command

The inbox screen can trigger an importer to transform pending files.
Configure the command in the config file:

```ini
[general]
import_cmd = python beancount-importer.py
```

### Version Control Tool

Press `V` to open a version control tool for the beancount ledger directory.
The default command is:

```ini
[general]
vc_cmd = tig -C $BEANCOUNT_LEDGER_DIR
```

Override the command in the config file to use a different tool.
The command is passed to the shell, so environment variables are expanded.
The TUI is suspended while the tool runs and resumes on exit.

### AI Account Prediction

Use an AI service like [bean-ai](https://github.com/samprintz/bean-ai)
to predict accounts based on narrations:

    bean-review input.beancount --ai-host localhost

The AI service should accept POST requests to `/predict`
with a JSON body containing `{"narrations": ["..."]}` and return `{"accounts": ["..."]}`.
