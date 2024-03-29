from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from pathlib import Path
from textual.widgets import (
    Button,
    Label,
    Select,
    Switch,
    RadioSet,
    RadioButton,
    Input,
    Markdown,
)

from tiny_code.config import ConfigManager
from tiny_code.consts import TEXT_AREA_COLOR_THEMES
from tiny_code.entities import Config
from typing import Optional, Literal


class HelpScreen(ModalScreen):
    MARKDOWN_HELP_MESSAGE = """\
## Keyboard shortcuts
### In all application
- **esc**       => *Exit the application*
- **f1**        => *Get help*
- **f12**       => *Set configs*
- **ctrl+b**    => *Show/Hide sidebar file manager*
### In file manager
- **delete**    => *Delete a file or directory*
- **insert**    => *Create a file or directory*
### In code editor
- **ctrl+z**    => *Undo changes*
- **ctrl+y**    => *Redo changes*
- **ctrl+a**    => *Select all lines from file*
- **ctrl+c**    => *Copy line/lines to clipboard*
- **ctrl+x**    => *Cut line/lines to clipboard*
- **ctrl+v**    => *Paste line/lines from clipboard*
- **ctrl+s**    => *Save file*
- **ctrl+/**    => *Comment/Uncomment line/lines*
- **tab**       => *Tab line/lines*
- **shift+tab** => *Untab line/lines*
"""

    def compose(self) -> ComposeResult:
        with ScrollableContainer(classes='modal'):
            with Horizontal(classes='row'):
                yield Markdown(self.MARKDOWN_HELP_MESSAGE, classes='col-12')
            with Horizontal(classes='row fixed-bottom ms-2'):
                yield Button(
                    'Close',
                    variant='error',
                    id='close',
                    classes='col-3',
                )

    @on(Button.Pressed, '#close')
    def close(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
        self.app.modal_screen_active = False


class ConfigsScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with ScrollableContainer(classes='modal'):
            with Horizontal(classes='row'):
                yield Label('Dark mode?', classes='col-3 mt-1')
                yield Switch(False, id='input-dark-mode', classes='col-2')
            with Horizontal(classes='row mt-1'):
                yield Label('Show line numbers?', classes='col-3 mt-1')
                yield Switch(
                    False, id='input-show-line-numbers', classes='col-2'
                )
            with Horizontal(classes='row mt-1'):
                yield Label('Break lines?', classes='col-3 mt-1')
                yield Switch(False, id='input-break-lines', classes='col-2')
            with Horizontal(classes='row mt-1'):
                yield Label('Theme:', classes='col-3 mt-1')
                yield Select.from_values(
                    TEXT_AREA_COLOR_THEMES,
                    allow_blank=False,
                    id='input-theme',
                    classes='col-9',
                )
            with Horizontal(classes='row mt-1'):
                yield Label('Tab size:', classes='col-3 mt-1')
                yield Select.from_values(
                    range(1, 9),
                    allow_blank=False,
                    value=4,
                    id='input-tab-size',
                    classes='col-9',
                )
            with Horizontal(classes='row align-left-bottom mt-1'):
                yield Button(
                    'Cancel',
                    variant='error',
                    id='cancel',
                    classes='col-3 me-1',
                )
                yield Button(
                    'Confirm',
                    variant='success',
                    id='confirm',
                    classes=' col-3 ms-1',
                )

    def on_mount(self) -> None:
        self.input_dark_mode = self.query_one(selector='#input-dark-mode')
        self.input_show_line_numbers = self.query_one(
            selector='#input-show-line-numbers'
        )
        self.input_break_lines = self.query_one(selector='#input-break-lines')
        self.input_theme = self.query_one(selector='#input-theme')
        self.input_tab_size = self.query_one(selector='#input-tab-size')

        current_config = ConfigManager.get()
        self.input_dark_mode.value = current_config.dark_mode
        self.input_show_line_numbers.value = current_config.show_line_numbers
        self.input_break_lines.value = current_config.break_lines
        self.input_theme.value = current_config.theme
        self.input_tab_size.value = current_config.tab_size

    @on(Button.Pressed, '#confirm')
    def confirm(self) -> None:
        ConfigManager.set(
            config=Config(
                dark_mode=self.input_dark_mode.value,
                show_line_numbers=self.input_show_line_numbers.value,
                break_lines=self.input_break_lines.value,
                theme=self.input_theme.value,
                tab_size=self.input_tab_size.value,
            )
        )
        self.app.dark = self.input_dark_mode.value
        self.app.text_area.show_line_numbers = (
            self.input_show_line_numbers.value
        )
        self.app.text_area.soft_wrap = self.input_break_lines.value
        self.app.text_area.theme = self.input_theme.value
        self.app.text_area.tab_size = self.input_tab_size.value
        self.app.pop_screen()
        self.app.modal_screen_active = False

    @on(Button.Pressed, '#cancel')
    def cancel(self) -> None:
        self.app.pop_screen()
        self.app.modal_screen_active = False


class CreateFileOrDirScreen(ModalScreen):
    def __init__(self, directory_path: Path) -> None:
        super().__init__()
        self.directory_path = directory_path

    def compose(self) -> ComposeResult:
        with ScrollableContainer(classes='modal'):
            with Horizontal(classes='row'):
                yield Label('Type: ', classes='col-3 mt-1')
                with RadioSet():
                    yield RadioButton(
                        '📄 File', id='input-type-file', value=True
                    )
                    yield RadioButton('📁 Directory', id='input-type-directory')
            with Horizontal(classes='row mt-1'):
                yield Label('Name: ', classes='col-3 mt-1')
                yield Input(id='input-name', classes='col-9')
            with Horizontal(classes='row align-left-bottom mt-1'):
                yield Button(
                    'Cancel',
                    variant='error',
                    id='cancel',
                    classes='col-3 me-1',
                )
                yield Button(
                    'Confirm',
                    variant='success',
                    id='confirm',
                    classes=' col-3 ms-1',
                )

    def on_mount(self) -> None:
        self.input_type_file = self.query_one(selector='#input-type-file')
        self.input_type_directory = self.query_one(
            selector='#input-type-directory'
        )
        self.input_name = self.query_one(selector='#input-name')

        self.input_type_selected: Optional[
            Literal['file', 'directory']
        ] = 'file'

    @on(RadioSet.Changed)
    def type_selected(self, event: RadioSet.Changed) -> None:
        if event.pressed.id == 'input-type-file':
            self.input_type_selected = 'file'
        elif event.pressed.id == 'input-type-directory':
            self.input_type_selected = 'directory'

    @on(Button.Pressed, '#confirm')
    def confirm(self) -> None:
        def create_file() -> None:
            try:
                new_file_path = self.directory_path.joinpath(
                    self.input_name.value.strip()
                )
                new_file_path.touch()
            except Exception:
                self.notify(
                    title='❌',
                    message=f'Fail to create file `{new_file_path}`.',
                    severity='error',
                    timeout=4,
                )
                self.app.bell()
            finally:
                self.app.dir_tree.reload()

        def create_dir() -> None:
            try:
                new_directory_path = self.directory_path.joinpath(
                    self.input_name.value.strip()
                )
                new_directory_path.mkdir()
            except Exception:
                self.notify(
                    title='❌',
                    message=f'Fail to create directory `{new_directory_path}`.',
                    severity='error',
                    timeout=4,
                )
                self.app.bell()
            finally:
                self.app.dir_tree.reload()

        if self.input_name.value.strip() == '':
            self.notify(
                title='❌',
                message=f'Name can not be empty.',
                severity='error',
                timeout=4,
            )
            self.app.bell()
            return

        if self.input_type_selected == 'file':
            create_file()
        elif self.input_type_selected == 'directory':
            create_dir()

        self.app.pop_screen()
        self.app.modal_screen_active = False

    @on(Button.Pressed, '#cancel')
    def cancel(self) -> None:
        self.app.pop_screen()
        self.app.modal_screen_active = False
