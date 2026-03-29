from pathlib import Path

from bean_review.util import scan_inbox


def test_scan_inbox_with_symlinked_inbox_dir(tmp_path: Path) -> None:
    """scan_inbox works when inbox_dir itself is a symlink.

    display_name must be relative to the symlink target, not contain
    the symlink path components.
    """
    real_dir = tmp_path / "real_inbox"
    real_dir.mkdir()
    (real_dir / "statement.csv").touch()

    link_dir = tmp_path / "link_inbox"
    link_dir.symlink_to(real_dir)

    entries = scan_inbox(str(link_dir))

    assert len(entries) == 1
    assert entries[0].display_name == "statement.csv"


def test_scan_inbox_with_symlinked_file(tmp_path: Path) -> None:
    """A symlinked file inside the inbox appears as a normal entry."""
    real_file = tmp_path / "elsewhere" / "statement.csv"
    real_file.parent.mkdir()
    real_file.touch()

    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    link_file = inbox_dir / "statement.csv"
    link_file.symlink_to(real_file)

    entries = scan_inbox(str(inbox_dir))

    assert len(entries) == 1
    assert entries[0].display_name == "statement.csv"


def test_scan_inbox_traverses_symlinked_subdir(tmp_path: Path) -> None:
    """scan_inbox follows symlinks to directories inside the inbox.

    A symlink inside the inbox that points to a directory must be traversed,
    and its files must appear in the result.
    """
    real_subdir = tmp_path / "external_folder"
    real_subdir.mkdir()
    (real_subdir / "statement.csv").touch()

    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    link_subdir = inbox_dir / "linked_folder"
    link_subdir.symlink_to(real_subdir)

    entries = scan_inbox(str(inbox_dir))

    assert len(entries) == 1
    assert entries[0].display_name == "linked_folder/statement.csv"
