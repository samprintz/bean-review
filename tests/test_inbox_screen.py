import pytest
from pathlib import Path

from bean_review.__main__ import ReviewerApp
from bean_review.config import load_config
from bean_review.screens.inbox_screen import InboxListItem, InboxScreen


INBOX_FILES = [
    "2026-03-28-checking-file-on-root.csv",
    "2026-03-28-checking-file-on-root.csv.beancount",
    "other-file-not-transformed-yet.csv",
    "subfolder/file-in-subfolder.pdf",
    "subfolder/file-in-subfolder.pdf.beancount",
    "sub/subfolder/2025-03-28-other-file-in-nested-subfolder.pdf",
    "sub/subfolder/2025-03-28-other-file-in-nested-subfolder.pdf.beancount",
]


def make_inbox(tmp_path: Path) -> None:
    for relative in INBOX_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


@pytest.mark.asyncio
async def test_inbox_screen_shows_entries(tmp_path: Path) -> None:
    make_inbox(tmp_path)
    app = ReviewerApp(load_config(None), inbox_dir=str(tmp_path))

    async with app.run_test() as pilot:
        assert isinstance(pilot.app.screen, InboxScreen)

        items = list(pilot.app.screen.query(InboxListItem))
        entries = [(item.entry.display_name, item.entry.is_reviewable) for item in items]

        assert entries == [
            ("2026-03-28-checking-file-on-root.csv", True),
            ("other-file-not-transformed-yet.csv", False),
            ("sub/subfolder/2025-03-28-other-file-in-nested-subfolder.pdf", True),
            ("subfolder/file-in-subfolder.pdf", True),
        ]
