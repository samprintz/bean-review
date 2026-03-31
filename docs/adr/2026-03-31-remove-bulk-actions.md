# Remove Bulk Import and Bulk Archive

The inbox screen originally offered two levels of import and archive:
a single-file action and a bulk action that passed the inbox directory
to a separate command (`import_all_cmd`, `archive_all_cmd`).

## Decision

Remove the bulk import and bulk archive actions.

## Consequences

- This prepares coupling the archive action
  to the "append to ledger" action,
  as both must always go together
  to prevent appending multiple times to ledger.
- The inbox screen is simpler: one import action, one archive action.
- Users configure a single `import_cmd` and `archive_cmd`.
