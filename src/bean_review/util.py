import os
import shlex
import subprocess
import sys
from collections.abc import Callable

from beancount import loader
from beancount.core import getters

from beancount.core.data import Transaction
from beancount.parser import parser

from .models import ReviewFile, ReviewTransaction, InboxEntry


def parse_file(input_path: str) -> list[Transaction]:
    """Parse transactions from a beancount file."""
    with open(input_path, 'r') as f:
        content = f.read()
    entries, errors, _ = parser.parse_string(content)

    if errors:
        for error in errors:
            print(f"Parse error: {error}", file=sys.stderr)

    return [e for e in entries if isinstance(e, Transaction)]


def create_review_file(transactions: list[Transaction], input_path: str) -> ReviewFile:
    """Create a ReviewFile from parsed transactions."""
    review_txns = [ReviewTransaction(directive=txn) for txn in transactions]
    filename = input_path.rsplit("/", 1)[-1] if "/" in input_path else input_path
    return ReviewFile(filename=filename, transactions=review_txns)


def scan_inbox(inbox_dir: str) -> list["InboxEntry"]:
    """Scan inbox directory; return one InboxEntry per non-.beancount file."""
    entries: list[InboxEntry] = []
    inbox_dir = os.path.abspath(inbox_dir)
    for root, _dirs, files in os.walk(inbox_dir, followlinks=True):
        for filename in sorted(files):
            if filename.endswith(".beancount"):
                continue
            abs_path = os.path.join(root, filename)
            beancount_path = abs_path + ".beancount"
            entries.append(InboxEntry(
                import_file=str(abs_path),
                beancount_file=str(beancount_path) if os.path.isfile(beancount_path) else None,
                inbox_root=inbox_dir,
            ))
    return sorted(entries, key=lambda e: e.display_name)


def run_archive(
    target: str,
    cmd_str: str,
    beancount_file: str | None = None,
    on_success: Callable[[], None] | None = None,
    on_error: Callable[[str], None] | None = None,
) -> None:
    """Run archive command; delete beancount_file and call on_success on exit 0."""
    cmd = shlex.split(cmd_str) + [target]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        if on_error:
            on_error(f"Archive failed (exit {result.returncode}).")
    else:
        if beancount_file and os.path.exists(beancount_file):
            os.remove(beancount_file)
        if on_success:
            on_success()


def load_accounts_from_ledger(ledger_path: str) -> list[str]:
    """Load account names from a beancount ledger file."""
    try:
        entries, errors, options = loader.load_file(ledger_path)
        return sorted(getters.get_accounts(entries))
    except Exception:
        return []
