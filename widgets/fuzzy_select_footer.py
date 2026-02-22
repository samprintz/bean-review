"""Fuzzy select footer widget for beancount-reviewer."""

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView


def fuzzy_match(query: str, text: str) -> bool:
    """Check if query fuzzy matches text (all chars appear in order)."""
    query, text = query.lower(), text.lower()
    qi = 0
    for char in text:
        if qi < len(query) and char == query[qi]:
            qi += 1
    return qi == len(query)


class FuzzySelectFooter(Widget):
    """Account selection with fuzzy search, suggestions appearing above input."""

    DEFAULT_CSS = """
    FuzzySelectFooter {
        dock: bottom;
        height: auto;
        max-height: 15;
        background: $surface;
        border-top: solid $primary;
    }

    FuzzySelectFooter #fuzzy-suggestions {
        height: auto;
        max-height: 10;
        background: $surface;
    }

    FuzzySelectFooter #fuzzy-suggestions > ListItem {
        padding: 0 1;
        height: 1;
    }

    FuzzySelectFooter #fuzzy-suggestions > ListItem.suggestion-selected {
        background: $accent;
    }

    FuzzySelectFooter #fuzzy-suggestions > ListItem.--highlight {
        background: $accent;
    }

    FuzzySelectFooter #fuzzy-input {
        height: 1;
        border: none;
        background: $surface;
        padding: 0 1;
    }

    FuzzySelectFooter #fuzzy-input:focus {
        border: none;
    }
    """

    class Selected(Message):
        """Message sent when user selects an option."""

        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    class Cancelled(Message):
        """Message sent when user cancels."""

        pass

    def __init__(
        self,
        options: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.options = options
        self._filtered_options: list[str] = []

    def compose(self) -> ComposeResult:
        yield ListView(id="fuzzy-suggestions")
        yield Input(placeholder="Escape to cancel", id="fuzzy-input")

    def on_mount(self) -> None:
        """Initialize suggestions list and focus input."""
        self._update_suggestions("")
        input_widget = self.query_one("#fuzzy-input", Input)
        input_widget.focus()

    def _update_suggestions(self, query: str) -> None:
        """Update the suggestions list based on query."""
        suggestions_view = self.query_one("#fuzzy-suggestions", ListView)
        suggestions_view.clear()

        if not self.options:
            return

        if query:
            self._filtered_options = [
                opt for opt in self.options if fuzzy_match(query, opt)
            ][:10]
        else:
            self._filtered_options = self.options[:10]

        for i, opt in enumerate(self._filtered_options):
            item = ListItem(Label(opt))
            if i == 0:
                item.add_class("suggestion-selected")
            suggestions_view.append(item)

        if self._filtered_options:
            suggestions_view.index = 0

    def _get_selected_suggestion(self) -> str | None:
        """Get the currently selected suggestion."""
        if not self._filtered_options:
            return None
        suggestions_view = self.query_one("#fuzzy-suggestions", ListView)
        if suggestions_view.index is not None and 0 <= suggestions_view.index < len(
            self._filtered_options
        ):
            return self._filtered_options[suggestions_view.index]
        return None

    def _update_selection_class(self) -> None:
        """Update the suggestion-selected class on list items."""
        suggestions_view = self.query_one("#fuzzy-suggestions", ListView)
        for i, item in enumerate(suggestions_view.children):
            if isinstance(item, ListItem):
                if i == suggestions_view.index:
                    item.add_class("suggestion-selected")
                else:
                    item.remove_class("suggestion-selected")

    def _move_suggestion_up(self) -> None:
        """Move selection up in suggestions list."""
        if not self._filtered_options:
            return
        suggestions_view = self.query_one("#fuzzy-suggestions", ListView)
        suggestions_view.action_cursor_up()
        self._update_selection_class()

    def _move_suggestion_down(self) -> None:
        """Move selection down in suggestions list."""
        if not self._filtered_options:
            return
        suggestions_view = self.query_one("#fuzzy-suggestions", ListView)
        suggestions_view.action_cursor_down()
        self._update_selection_class()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for fuzzy search."""
        if event.input.id == "fuzzy-input":
            self._update_suggestions(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "fuzzy-input":
            suggestion = self._get_selected_suggestion()
            value = suggestion if suggestion else event.value.strip()
            if value:
                self.post_message(self.Selected(value))
            else:
                self.post_message(self.Cancelled())
            event.prevent_default()
            event.stop()

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.post_message(self.Cancelled())
            event.prevent_default()
            event.stop()
        elif event.key == "up":
            self._move_suggestion_up()
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            self._move_suggestion_down()
            event.prevent_default()
            event.stop()
        elif event.key == "tab":
            # Tab completes with selected suggestion
            suggestion = self._get_selected_suggestion()
            if suggestion:
                input_widget = self.query_one("#fuzzy-input", Input)
                input_widget.value = suggestion
                input_widget.cursor_position = len(suggestion)
            event.prevent_default()
            event.stop()
