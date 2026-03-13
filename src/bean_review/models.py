from dataclasses import dataclass, field

from beancount import loader
from beancount.core import getters
from beancount.core.data import Transaction


@dataclass
class ReviewTransaction:
    """A transaction wrapper for review state."""

    directive: Transaction
    selected: bool = False

    @property
    def is_complete(self) -> bool:
        """Check if transaction is marked as complete (flag='*')."""
        return self.directive.flag == "*"

    @property
    def date(self):
        """Get transaction date."""
        return self.directive.date

    @property
    def payee(self) -> str | None:
        """Get transaction payee."""
        return self.directive.payee

    @property
    def narration(self) -> str:
        """Get transaction narration."""
        return self.directive.narration

    @property
    def postings(self):
        """Get transaction postings."""
        return self.directive.postings

    def toggle_complete(self) -> "ReviewTransaction":
        """Toggle between complete ('*') and incomplete ('!') flags."""
        new_flag = "!" if self.is_complete else "*"
        new_directive = self.directive._replace(flag=new_flag)
        return ReviewTransaction(directive=new_directive, selected=self.selected)

    def with_directive(self, directive: Transaction) -> "ReviewTransaction":
        """Return a new ReviewTransaction with updated directive."""
        return ReviewTransaction(directive=directive, selected=self.selected)


@dataclass
class ReviewFile:
    """A group of transactions from the same source file."""

    filename: str
    transactions: list[ReviewTransaction] = field(default_factory=list)

    @property
    def complete_count(self) -> int:
        """Count of complete transactions."""
        return sum(1 for t in self.transactions if t.is_complete)

    @property
    def total_count(self) -> int:
        """Total number of transactions."""
        return len(self.transactions)

    @property
    def incomplete_count(self) -> int:
        """Count of incomplete transactions."""
        return self.total_count - self.complete_count

    @property
    def has_incomplete(self) -> bool:
        """Check if file has any incomplete transactions."""
        return self.incomplete_count > 0


def load_accounts_from_ledger(ledger_path: str) -> list[str]:
    """Load account names from a beancount ledger file."""
    try:
        entries, errors, options = loader.load_file(ledger_path)
        return sorted(getters.get_accounts(entries))
    except Exception:
        return []
