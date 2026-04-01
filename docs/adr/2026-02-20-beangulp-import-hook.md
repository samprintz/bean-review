# Not as Beangulp Import Hook

`beangulp` supports import hooks where the imported transactions could be edited:

```python
from beangulp import Ingest
from beangulp_reviewer import review_hook

ingest = Ingest(
    importers=[...],
    hooks=[review_hook],
)

ingest()
```

## Decision

Keep the UI as a separate review step after ingestion.
Do not embed a `textual` TUI as a beangulp hook.

## Rationale

### Pro

- **Separation of concerns**: Beangulp's job is to convert raw data to Beancount entries
  (not human review and edit of transactions).
- **Testing** the ingestion requires launching the UI.
- **Failure recovery**: If the UI crashes, you lose the entire ingest run and in-memory state.
- **Cleaner data flow**: Intermediate artifacts (like a draft file) enable better workflows and audit trails.

### Drawback

- Access to **meta information** during ingestion (e.g. importer name, file name)
