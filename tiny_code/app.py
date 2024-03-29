from pathlib import Path

from textual import on
from textual.app import App, Binding, ComposeResult
from textual.widgets import Footer, Header

from tiny_code.config import ConfigManager
from tiny_code.consts import STYLE_TCSS_PATH
from tiny_code.custom_widgets import CustomDirectoryTree, CustomTextArea
from tiny_code.modal_screens import (
    ConfigsScreen,
    CreateFileOrDirScreen,
    HelpScreen,
)
from tiny_code.utils import remove_dir_or_file


class TinyCodeApp(App, inherit_bindings=False):
    CSS = STYLE_TCSS_PATH.read_text()
    TITLE = 'TinyCode'
    SUB_TITLE = 'Simple and stupid code editor'
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding(
            key='escape',
            action='quit()',
            description='Exit',
            show=True,
            priority=True,
        ),
        Binding(
            key='f1',
            action='show_modal_help()',
            description='Help',
            show=True,
            priority=True,
        ),
        Binding(
            key='f12',
            action='show_modal_configs()',
            description='Configs',
            show=False,
            priority=True,
        ),
        Binding(
            key='ctrl+b',
            action='toggle_directory_tree_visibility()',
            description='Show|Hide directory tree',
            show=False,
            priority=True,
        ),
    ]

    def __init__(self, dir_path: Path):
        super().__init__()
        self.dir_path = dir_path
        self.modal_screen_active: bool = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield CustomDirectoryTree(self.dir_path)
        yield CustomTextArea()
        yield Footer()

    def on_mount(self) -> None:
        self.dir_tree = self.query_one(selector=CustomDirectoryTree)
        self.text_area = self.query_one(selector=CustomTextArea)

        current_config = ConfigManager.get()
        self.text_area.theme = current_config.theme
        self.text_area.tab_size = current_config.tab_size

    @on(CustomDirectoryTree.FileSelected)
    def on_file_selected(
        self, event: CustomDirectoryTree.FileSelected
    ) -> None:
        LANGUAGES_MAP = {
            '.py': 'python',
            '.json': 'json',
            '.toml': 'toml',
            '.html': 'html',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.css': 'css',
        }
        file_selected = event.path.resolve()
        if not file_selected.is_file():
            self.notify(
                title='❌',
                message=f'File `{str(file_selected)}` not exists or is not a file.',
                severity='error',
                timeout=10,
            )
            self.bell()
            self.dir_tree.reload()
            return

        self.text_area.border_title = f'Code editor - {file_selected.name}'
        self.file_selected = file_selected
        language_syntax = LANGUAGES_MAP.get(
            self.file_selected.suffix.lower(), None
        )
        try:
            self.text_area.load_text(self.file_selected.read_text())
            self.text_area.language = language_syntax
        except Exception:
            self.text_area.load_text(str(self.file_selected.read_bytes()))
            self.text_area.language = language_syntax

    @on(CustomDirectoryTree.FileDeleteRequested)
    def on_file_deleted(
        self, event: CustomDirectoryTree.FileDeleteRequested
    ) -> None:
        file_selected = event.path
        if not file_selected.is_file():
            self.notify(
                title='❌',
                message=f'File `{str(file_selected)}` not exists or is not a file.',
                severity='error',
                timeout=10,
            )
            self.bell()
            self.dir_tree.reload()
            return

        try:
            remove_dir_or_file(dir_or_file_path=file_selected)
        except Exception:
            self.notify(
                title='❌',
                message=f'Fail to delete `{str(file_selected)}`.',
                severity='error',
                timeout=10,
            )
            self.bell()
        finally:
            self.dir_tree.reload()

    @on(CustomDirectoryTree.DirectoryDeleteRequested)
    def on_directory_deleted(
        self, event: CustomDirectoryTree.DirectoryDeleteRequested
    ) -> None:
        directory_selected = event.path
        if not directory_selected.is_dir():
            self.notify(
                title='❌',
                message=f'Directory `{str(directory_selected)}` not exists or is not a directory.',
                severity='error',
                timeout=10,
            )
            self.bell()
            self.dir_tree.reload()
            return
        if (
            not directory_selected.is_writable()
            or not directory_selected.is_executable()
        ):
            self.notify(
                title='❌',
                message=f'You need write and execute permission on the directory `{str(directory_selected)}`',
                severity='error',
                timeout=10,
            )
            self.bell()
            self.dir_tree.reload()
            return
        if (
            not directory_selected.parent.is_writable()
            or not directory_selected.parent.is_executable()
        ):
            self.notify(
                title='❌',
                message=f'You need write and execute permission on the directory `{str(directory_selected.parent)}`',
                severity='error',
                timeout=10,
            )
            self.bell()
            self.dir_tree.reload()
            return

        has_errors = False
        for path in directory_selected.rglob('*'):
            if not path.is_writable() or not path.is_executable():
                has_errors = True
                self.notify(
                    title='❌',
                    message=f'You need write and execute permission on the directory `{str(path)}`',
                    severity='error',
                    timeout=10,
                )

        if has_errors:
            self.bell()
            self.dir_tree.reload()
            return

        try:
            remove_dir_or_file(dir_or_file_path=directory_selected)
        except Exception as error:
            self.notify(
                title='❌',
                message=f'Fail to delete `{str(directory_selected)}`| {str(error)}.',
                severity='error',
                timeout=10,
            )
            self.bell()
        finally:
            self.dir_tree.reload()

    @on(CustomDirectoryTree.FileOrDirectoryCreateRequested)
    def on_file_or_dir_created(
        self, event: CustomDirectoryTree.FileOrDirectoryCreateRequested
    ) -> None:
        if self.modal_screen_active:
            return
        self.push_screen(CreateFileOrDirScreen(directory_path=event.path))
        self.modal_screen_active = True

    @on(CustomTextArea.SaveRequested)
    def on_file_saved(self, event: CustomTextArea.SaveRequested) -> None:
        if isinstance(event.content, str):
            self.file_selected.write_text(event.content)
        elif isinstance(event.content, bytes):
            self.file_selected.write_bytes(event.content)

    def action_toggle_directory_tree_visibility(self) -> None:
        if self.dir_tree.styles.display == 'none':
            self.dir_tree.styles.display = 'block'
        elif self.dir_tree.styles.display == 'block':
            self.dir_tree.styles.display = 'none'

    def action_show_modal_configs(self) -> None:
        if self.modal_screen_active:
            return
        self.push_screen(screen=ConfigsScreen())
        self.modal_screen_active = True

    def action_show_modal_help(self) -> None:
        if self.modal_screen_active:
            return
        self.push_screen(screen=HelpScreen())
        self.modal_screen_active = True
