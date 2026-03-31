# CLAUDE.md

This file provides guidance to Claude Code
when working with code in this repository.

## Project Overview

See `PROJECT_SPEC.md` for the project specification.

## Instructions

### Project specification and documentation

The project specification and documentation must be kept up-to-date.

Whenever you change code, check the project specification in `PROJECT_SPEC.md`,
and all `*.md` documents, especially in `docs/` and `adr/`.

Documents, that are affected by your changes
must be updated.

Major design decisions
must be recorded in a new Architecture Design Record (ADR) in `adr/`.

### Git commit messages

Git commit messages must follow the
Conventional Commit message style.

Use only scopes that are defined in `docs/scopes.md`
or no scope.

The message should follow the pattern
of other commit messages in the Git repo.
Inspect recent commit message style with
`git -C "/path/to/repo" --no-pager log -n 8 --pretty=format:"%s"`
(do not use `cd`).

Do not use `git status`,
but write the commit message based on
insights from the conversion.

The commit message should be
rather about *why* than the *what* of the changes.

If you have no information about *why*,
don't make assumptions but write about *what* then.

The title of the message MUST be less than 72 chars.
Add a commit message body only if required
for a comprehensible description or
to explain the *why* of important design decisions.

### Line length

Limit all code lines you write to approx. 80 chars, max. 100 chars.
