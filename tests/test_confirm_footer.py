import pytest
from textual.app import App, ComposeResult

from bean_review.widgets import ConfirmFooter


class _ConfirmApp(App):
    def __init__(self, on_success, on_reject) -> None:
        super().__init__()
        self._on_success = on_success
        self._on_reject = on_reject

    def compose(self) -> ComposeResult:
        yield ConfirmFooter(
            message="Delete?",
            on_success=self._on_success,
            on_reject=self._on_reject,
            id="footer",
        )

    def on_mount(self) -> None:
        self.query_one(ConfirmFooter).focus()


@pytest.mark.asyncio
async def test_confirm_footer_shows_message() -> None:
    app = _ConfirmApp(on_success=lambda: None, on_reject=lambda: None)
    async with app.run_test() as pilot:
        footer = pilot.app.query_one("#footer", ConfirmFooter)
        assert footer.message == "Delete?"


@pytest.mark.asyncio
async def test_confirm_footer_y_calls_on_success() -> None:
    called: list[str] = []
    app = _ConfirmApp(
        on_success=lambda: called.append("success"),
        on_reject=lambda: called.append("reject"),
    )
    async with app.run_test() as pilot:
        await pilot.press("y")
        await pilot.pause()
        assert called == ["success"]


@pytest.mark.asyncio
async def test_confirm_footer_n_calls_on_reject() -> None:
    called: list[str] = []
    app = _ConfirmApp(
        on_success=lambda: called.append("success"),
        on_reject=lambda: called.append("reject"),
    )
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert called == ["reject"]


@pytest.mark.asyncio
async def test_confirm_footer_escape_calls_on_reject() -> None:
    called: list[str] = []
    app = _ConfirmApp(
        on_success=lambda: called.append("success"),
        on_reject=lambda: called.append("reject"),
    )
    async with app.run_test() as pilot:
        await pilot.press("escape")
        await pilot.pause()
        assert called == ["reject"]
