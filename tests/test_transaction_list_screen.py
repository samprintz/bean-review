import pytest
from pathlib import Path

from bean_review.__main__ import ReviewerApp
from bean_review.config import Config
from bean_review.screens.transaction_list_screen import TransactionListScreen
from bean_review.util import create_review_file, parse_file


MINIMAL_BEANCOUNT = """\
2026-01-01 * "Supermarket" ""
  Expenses:Food  10.00 EUR
  Assets:Checking  -10.00 EUR
"""


def make_beancount_file(path: Path, content: str = MINIMAL_BEANCOUNT) -> None:
    path.write_text(content)


@pytest.mark.asyncio
async def test_append_and_archive_deletes_beancount_file(
    tmp_path: Path,
) -> None:
    """append_and_archive must delete the .beancount file on success."""
    import_file = tmp_path / "bank.csv"
    beancount = tmp_path / "bank.csv.beancount"
    import_file.touch()
    make_beancount_file(beancount)

    ledger = tmp_path / "ledger.beancount"
    ledger.touch()
    config = Config(
        ledger_file=str(ledger),
        archive_cmd="echo",
    )

    transactions = parse_file(str(beancount))
    review_file = create_review_file(transactions, str(beancount))

    app = ReviewerApp(
        config,
        review_file=review_file,
        source_file=str(beancount),
    )

    async with app.run_test() as pilot:
        screen = pilot.app.screen
        assert isinstance(screen, TransactionListScreen)

        # Inject inbox_import_file so append_and_archive is available
        screen._inbox_import_file = str(import_file)
        screen._back_to_inbox = False

        assert beancount.exists()

        screen._append_and_archive()
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        await pilot.pause()

        assert not beancount.exists()
