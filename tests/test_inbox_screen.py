import pytest
from pathlib import Path

from textual.widgets import ListView

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


@pytest.mark.asyncio
async def test_entry_selection_preserved_after_reload(tmp_path: Path) -> None:
    make_inbox(tmp_path)
    app = ReviewerApp(load_config(None), inbox_dir=str(tmp_path))

    async with app.run_test() as pilot:
        assert isinstance(pilot.app.screen, InboxScreen)
        screen = pilot.app.screen

        # Navigate to the second entry (index 1)
        await pilot.press("down")
        await pilot.pause()

        list_view = screen.query_one("#inbox-list", ListView)
        assert list_view.index == 1

        # Simulate what happens after import: reload the list
        await screen._reload()
        await pilot.pause()

        # The selection should remain at index 1, not jump back to 0
        assert list_view.index == 1
        # The item at index 1 must be visually highlighted
        assert list_view.highlighted_child is not None
        assert list_view.highlighted_child.highlighted is True


@pytest.mark.asyncio
async def test_refresh_inbox(tmp_path: Path) -> None:
    make_inbox(tmp_path)
    app = ReviewerApp(load_config(None), inbox_dir=str(tmp_path))

    async with app.run_test() as pilot:
        assert isinstance(pilot.app.screen, InboxScreen)

        # Verify initial count
        items_before = list(pilot.app.screen.query(InboxListItem))
        assert len(items_before) == 4

        # Add a new import file to the inbox while the app is running
        new_file = tmp_path / "new-import.csv"
        new_file.touch()

        await pilot.press("f5")
        await pilot.pause()

        items_after = list(pilot.app.screen.query(InboxListItem))
        display_names = [item.entry.display_name for item in items_after]
        assert "new-import.csv" in display_names
        assert len(items_after) == 5
