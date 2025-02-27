import os
from rich.syntax import Syntax
from rich.table import Table

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import RichLog, Tabs, Tab, Static, Input, TabbedContent, TabPane


# ======================================================================================================================
class SuggestionBoxWidget(Static):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, suggestions: list):
        super().update(f"Suggestions: {', '.join(suggestions)}" if suggestions else "")


# ======================================================================================================================
class CommandInputWidget(Input):
    ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------------------------------------------------------
    def on_mount(self) -> None:
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def on_key(self, event: events.Key) -> None:
        self.parent.on_key(event)
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
class CommandWidget(Widget):
    input_widget: Input
    suggestions_box: SuggestionBoxWidget

    commands: list
    command_history: list
    history_index: int
    suggestions_box: (Static, Widget) = None

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, use_suggestion_box, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_widget = Input(placeholder=">> ")

        if use_suggestion_box:
            self.suggestions_box = Static(id="suggestions-box", expand=False)

    # ------------------------------------------------------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        with Vertical():
            if self.suggestions_box:
                yield self.suggestions_box
            yield self.input_widget

    # ------------------------------------------------------------------------------------------------------------------
    def setCommands(self, commands: list):
        self.commands = commands

    # ------------------------------------------------------------------------------------------------------------------
    def on_key(self, event: events.Key) -> None:
        ...

# class CommandInput(Input):
#     """Custom Input widget with command history and suggestions."""
#     commands = [
#         "start", "stop", "restart", "status", "help",
#         "exit", "deploy", "rollback", "update", "configure",
#     ]
#     command_history = []
#     history_index = -1
#     suggestions_box: (Static, Widget) = None
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def on_mount(self) -> None:
#         """Mount and initialize the suggestions box."""
#         self.suggestions_box = self.app.query_one("#suggestions-box")
#         self.suggestions_box.update(f"Suggestions: {', '.join(self.commands)}")
#
#     def on_key(self, event: events.Key) -> None:
#         """Handle key events for command history and suggestions."""
#         if event.key == "up":
#             if self.command_history and self.history_index > 0:
#                 self.history_index -= 1
#                 self.value = self.command_history[self.history_index]
#                 self.cursor_position = len(self.value)
#         elif event.key == "down":
#             if self.command_history and self.history_index < len(self.command_history) - 1:
#                 self.history_index += 1
#                 self.value = self.command_history[self.history_index]
#                 self.cursor_position = len(self.value)
#             else:
#                 self.history_index = len(self.command_history)
#                 self.value = ""
#         elif event.key == "enter":
#             if self.value.strip():
#                 self.command_history.append(self.value)
#                 self.history_index = len(self.command_history)
#
#             value = ""
#             matches = [cmd for cmd in self.commands if cmd.startswith(value)]
#             self.suggestions_box.update(f"Suggestions: {', '.join(matches)}" if matches else "")
#         elif event.key == "tab":
#
#             matches = [cmd for cmd in self.commands if cmd.startswith(self.value)]
#             self.suggestions_box.update(f"Suggestions: {', '.join(matches)}" if matches else "")
#
#         elif event.key == 'backspace':
#             value = self.value[:-1]
#             matches = [cmd for cmd in self.commands if cmd.startswith(value)]
#             self.suggestions_box.update(f"Suggestions: {', '.join(matches)}" if matches else "")
#         else:
#             text_log = self.app.query_one(RichLog)
#
#             if len(event.key) == 1 and event.key.isalnum():
#                 value = self.value + event.key
#             else:
#                 value = self.value
#             matches = [cmd for cmd in self.commands if cmd.startswith(value)]
#             self.suggestions_box.update(f"Suggestions: {', '.join(matches)}" if matches else "")


# ======================================================================================================================
def LogWidget(RichLog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
