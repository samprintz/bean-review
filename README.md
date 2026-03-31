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

```bash
bean-review <input_file>       # open a .beancount file directly
bean-review <inbox_dir>        # open inbox screen for staged files
bean-review <(python import.py extract $BEANCOUNT_IMPORT_DIR)  # read from beangulp
```

## Configuration

Default config: `~/.config/beancount/bean-review.conf`
Override with `--config`.

### Export to main ledger

Priority for resolving the main ledger file (descending):

1. CLI: `--ledger-file`
2. Config: `ledger_file`
3. Environment: `BEANCOUNT_FILE`

```ini
[general]
ledger_file = ~/ledger/main.beancount
```

### Import with beangulp

Configure the import command to transform pending inbox files:

```ini
[general]
import_cmd = python my-beancount-importer.py
import_all_cmd = python my-beancount-importer.py --all
```

`import_cmd` is used for single-file import and as fallback for bulk import.
`import_all_cmd` is used for bulk import.

### Version control

Opens a version control tool for the beancount ledger directory (e.g. `tig`):

```ini
[general]
version_control_cmd = tig -C $BEANCOUNT_LEDGER_DIR
```

The command is passed to the shell, so environment variables are expanded.

### AI account prediction

Use an AI service like [bean-ai](https://github.com/samprintz/bean-ai)
to predict accounts based on narrations:

```bash
bean-review input.beancount --ai-host localhost
```

The AI service must accept `POST /predict`
with `{"narrations": ["..."]}`
and return `{"accounts": ["..."]}`.
