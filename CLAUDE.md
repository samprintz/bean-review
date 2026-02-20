# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`beancount-reviewer` is a Python application.
It is a TUI.
It allows the user to manually review transactions.

The application reads transactions from stdin and writes the reviewed transactions to stdout.

Transactions are in Beancount format (https://beancount.github.io/docs/beancount_language_syntax.html):

```
2002-02-20 * "Grocery store"
  Assets:Cash      -5.99 EUR
  Expenses:Food     5.99 EUR
```

Use `beancount` module for parsing and handling transactions,
e.g. `beancount.loader` or `beancount.parser.printer`.
It uses the types provided by `beancount` for transactions, postings, etc.,
see `beancount.core.data`.

Use `textual` as TUI module.
