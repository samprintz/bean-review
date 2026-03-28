import os
from dataclasses import dataclass, field

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


@dataclass
class InboxEntry:
    """An import file in the inbox with an optional beancount counterpart."""

    import_file: str        # absolute path (CSV, PDF, …)
    beancount_file: str | None  # absolute path to <import_file>.beancount, or None
    inbox_root: str         # absolute path to inbox root

    @property
    def display_name(self) -> str:
        """Path relative to inbox root."""
        return os.path.relpath(self.import_file, self.inbox_root)

    @property
    def is_reviewable(self) -> bool:
        """Whether this entry has a corresponding beancount file."""
        return self.beancount_file is not None
