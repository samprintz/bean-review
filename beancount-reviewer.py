#!/usr/bin/env python3

import argparse
import sys

from beancount.core.data import Transaction
from beancount.parser import parser, printer
from textual.app import App
from textual.theme import Theme

from config import Config, load_config
from models import ReviewFile, ReviewTransaction
from screens import TransactionListScreen

plain_light_theme = Theme(
    name="plain-light",
    primary="#555555",
    secondary="#dddddd",
    accent="#888888",
    foreground="#000000",
    background="#ffffff",
    success="#557755",
    warning="#887755",
    error="#c73030",
    surface="#f5f5f5",
    panel="#eeeeee",
    dark=False,
)


class ReviewerApp(App):
    TITLE = "Beancount Reviewer"

    def __init__(
        self,
        review_file: ReviewFile,
        config: Config,
    ) -> None:
        super().__init__()
        self.review_file = review_file
        self.config = config
        self.should_save = False

    def on_mount(self) -> None:
        self.register_theme(plain_light_theme)
        self.theme = "plain-light"
        self.push_screen(TransactionListScreen(self.review_file, self.config))

    def save_and_exit(self) -> None:
        """Mark for save and exit the application."""
        self.should_save = True
        self.exit()


def parse_file(input_path: str) -> list[Transaction]:
    """Parse transactions from a file."""
    with open(input_path, 'r') as f:
        content = f.read()
    entries, errors, _ = parser.parse_string(content)

    if errors:
        for error in errors:
            print(f"Parse error: {error}", file=sys.stderr)

    return [e for e in entries if isinstance(e, Transaction)]


def create_review_file(
    transactions: list[Transaction], input_path: str
) -> ReviewFile:
    """Create a ReviewFile from parsed transactions."""
    review_txns = [ReviewTransaction(directive=txn) for txn in transactions]
    # Use basename for display
    filename = input_path.rsplit("/", 1)[-1] if "/" in input_path else input_path
    return ReviewFile(filename=filename, transactions=review_txns)


def output_transactions(review_file: ReviewFile) -> None:
    """Output all transactions to stdout."""
    for review_txn in review_file.transactions:
        print(printer.format_entry(review_txn.directive))


def main() -> None:
    """Main entry point."""
    arg_parser = argparse.ArgumentParser(
        description="Review beancount transactions in a TUI"
    )
    arg_parser.add_argument(
        "input_file",
        help="Input beancount file with transactions to review",
    )
    arg_parser.add_argument(
        "--config",
        default=None,
        help="Path to config file (default: ~/.config/beancount/bean-review.conf)",
    )
    arg_parser.add_argument(
        "--ledger-file",
        default=None,
        help="Path to main ledger file for account completion",
    )
    args = arg_parser.parse_args()

    config = load_config(args.config, ledger_file_override=args.ledger_file)

    transactions = parse_file(args.input_file)

    if not transactions:
        print("No transactions found in input.", file=sys.stderr)
        sys.exit(1)

    review_file = create_review_file(transactions, args.input_file)

    app = ReviewerApp(review_file, config)
    app.run()

    if app.should_save:
        output_transactions(app.review_file)


if __name__ == "__main__":
    main()
