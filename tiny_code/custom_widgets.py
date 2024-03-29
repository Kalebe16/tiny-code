from pathlib import Path
from typing import Optional, Union, Iterable

import pyperclip
from rich.style import Style
from rich.text import Text
from textual.events import Key
from textual.message import Message
from textual.widgets import DirectoryTree, TextArea
from textual.widgets._directory_tree import TOGGLE_STYLE, DirEntry, TreeNode

from tiny_code.utils import (
    find_first_char_non_void,
    find_last_char_non_void,
    tab_text,
    comment_or_uncomment_text,
)
from tiny_code.consts import INLINE_COMMENT_CHAR_MAP


class CustomTextArea(TextArea):
    BORDER_TITLE = 'Code editor'

    class SaveRequested(Message):
        def __init__(
            self,
            content: Union[str, bytes],
        ) -> None:
            super().__init__()
            self.content = content

    def __init__(self) -> None:
        self.tab_size: int = None
        super().__init__(show_line_numbers=True, soft_wrap=False)

    async def _on_key(self, event: Key) -> None:
        if event.character in ['(', '[', '{', "'", '"']:
            self.handle_bracket_insertion(event=event)
        elif event.key == 'ctrl+c':
            self.handle_copy(event=event)
        elif event.key == 'ctrl+s':
            self.handle_save(event=event)
        elif event.key == 'ctrl+v':
            self.handle_paste(event=event)
        elif event.key == 'ctrl+a':
            self.handle_select_all(event=event)
        elif event.key in ['tab', 'shift+tab']:
            self.handle_indentation(event=event)
        elif event.key == 'ctrl+underscore':
            self.handle_comment(event=event)
        else:
            self.handle_default_bindings(event=event)

    def handle_bracket_insertion(self, event: Key) -> None:
        BRACKETS_MAP = {
            '(': '()',
            '[': '[]',
            '{': '{}',
            "'": "''",
            '"': '""',
        }
        self.insert(BRACKETS_MAP.get(event.character))
        self.move_cursor_relative(columns=-1)
        event.prevent_default()

    def handle_copy(self, event: Key) -> None:
        def copy_line() -> None:
            cursor_line, _ = self.cursor_location
            line_content_original = self.document.get_line(cursor_line)
            pyperclip.copy(text=line_content_original)
            event.prevent_default()

        def copy_lines() -> None:
            pyperclip.copy(text=self.selected_text)
            event.prevent_default()

        if self.selected_text.strip() == '':
            copy_line()
        else:
            copy_lines()

    def handle_save(self, event: Key) -> None:
        self.post_message(
            self.SaveRequested(
                content=self.text,
            )
        )
        event.prevent_default()

    def handle_paste(self, event: Key) -> None:
        paste_content = pyperclip.paste()
        self.insert(text=paste_content, location=self.cursor_location)

    def handle_select_all(self, event: Key) -> None:
        self.select_all()
        event.prevent_default()

    def handle_indentation(self, event: Key) -> None:
        def tab_line() -> None:
            cursor_line, _ = self.cursor_location
            line_content_original = self.document.get_line(cursor_line)
            line_content_modified = tab_text(
                text=line_content_original,
                action=event.key,
                tab_size=self.tab_size,
            )
            self.replace(
                insert=line_content_modified,
                start=(cursor_line, 0),
                end=(cursor_line, len(line_content_original)),
            )
            self.move_cursor(
                (
                    cursor_line,
                    find_first_char_non_void(line_content_modified)
                    if event.key == 'tab'
                    else find_last_char_non_void(line_content_modified),
                )
            )
            event.prevent_default()

        def tab_lines() -> None:
            selected_text_start, selected_text_end = self.selection
            selected_text_start, selected_text_end = sorted(
                (selected_text_start, selected_text_end)
            )
            selected_text_start_line, selected_text_start_column = (
                selected_text_start[0],
                selected_text_start[1],
            )
            selected_text_end_line, selected_text_end_column = (
                selected_text_end[0],
                selected_text_end[1],
            )
            lines_content_original = self.document.get_text_range(
                start=(selected_text_start_line, 0),
                end=(
                    selected_text_end_line,
                    find_last_char_non_void(
                        self.document.get_line(selected_text_end_line)
                    ),
                ),
            )
            lines_content_modified = tab_text(
                text=lines_content_original,
                action=event.key,
                tab_size=self.tab_size,
            )
            self.replace(
                insert=lines_content_modified,
                start=(selected_text_start_line, 0),
                end=(
                    selected_text_end_line,
                    find_last_char_non_void(
                        self.document.get_line(selected_text_end_line)
                    ),
                ),
            )
            event.prevent_default()

        if self.selected_text.strip() == '':
            tab_line()
        else:
            tab_lines()

    def handle_comment(self, event: Key) -> None:
        def comment_line() -> None:
            cursor_line, _ = self.cursor_location
            line_content_original = self.document.get_line(cursor_line)
            line_content_modified = comment_or_uncomment_text(
                text=line_content_original, comment_char='#'
            )
            self.replace(
                insert=line_content_modified,
                start=(
                    cursor_line,
                    0,
                ),
                end=(
                    cursor_line,
                    find_last_char_non_void(line_content_original),
                ),
            )
            event.prevent_default()

        def comment_lines() -> None:
            selected_text_start, selected_text_end = self.selection
            selected_text_start, selected_text_end = sorted(
                (selected_text_start, selected_text_end)
            )
            selected_text_start_line, selected_text_start_column = (
                selected_text_start[0],
                selected_text_start[1],
            )
            selected_text_end_line, selected_text_end_column = (
                selected_text_end[0],
                selected_text_end[1],
            )
            lines_content_original = self.document.get_text_range(
                start=(selected_text_start_line, 0),
                end=(
                    selected_text_end_line,
                    find_last_char_non_void(
                        self.document.get_line(selected_text_end_line)
                    ),
                ),
            )
            lines_content_modified = comment_or_uncomment_text(
                text=lines_content_original, comment_char='#'
            )
            self.replace(
                insert=lines_content_modified,
                start=(selected_text_start_line, 0),
                end=(
                    selected_text_end_line,
                    find_last_char_non_void(
                        self.document.get_line(selected_text_end_line)
                    ),
                ),
            )
            event.prevent_default()

        if self.selected_text.strip() == '':
            comment_line()
        else:
            comment_lines()

    def handle_default_bindings(self, event: Key) -> None:
        IGNORE_DEFAULT_BINDINGS = [
            'f6',
            'f7',
            'ctrl+left',
            'ctrl+right',
            'ctrl+shift+left',
            'ctrl+shift+right',
            'ctrl+a',
            'ctrl+e',
            'ctrl+k',
            'ctrl+u',
            'ctrl+f',
            'ctrl+d',
            'ctrl+w',
            'shift+home',
            'shift+end',
            'tab',
        ]
        if event.key in IGNORE_DEFAULT_BINDINGS:
            event.prevent_default()
        else:
            super()._on_key(event=event)


class CustomDirectoryTree(DirectoryTree):
    BORDER_TITLE = 'File manager'

    class FileOrDirectoryCreateRequested(Message):
        def __init__(
            self,
            node: TreeNode[DirEntry],
            path: Path,
            parent_path: Optional[Path],
        ) -> None:
            super().__init__()
            self.node = node
            self.parent_path = parent_path
            self.path = path

    class FileDeleteRequested(Message):
        def __init__(
            self,
            node: TreeNode[DirEntry],
            path: Path,
            parent_path: Optional[Path],
        ) -> None:
            super().__init__()
            self.node = node
            self.parent_path = parent_path
            self.path = path

    class DirectoryDeleteRequested(Message):
        def __init__(
            self,
            node: TreeNode[DirEntry],
            path: Path,
            parent_path: Optional[Path],
        ) -> None:
            super().__init__()
            self.node = node
            self.parent_path = parent_path
            self.path = path

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path)
        self.guide_depth = 2

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        filtered_paths = [path for path in paths if path.name != '.git']
        return filtered_paths

    async def _on_key(self, event: Key) -> None:
        if event.key == 'delete':
            self.handle_delete(event=event)
        elif event.key == 'insert':
            self.handle_create(event=event)
        else:
            self.handle_default_bindings(event=event)

    def handle_delete(self, event: Key) -> None:
        current_node = self.cursor_node
        if self.cursor_node.parent and self.cursor_node.parent.data:
            current_selected_parent_path = self.cursor_node.parent.data.path
        else:
            current_selected_parent_path = None
        current_selected_path = self.cursor_node.data.path
        if current_selected_path.is_file():
            self.post_message(
                self.FileDeleteRequested(
                    node=current_node,
                    parent_path=current_selected_parent_path,
                    path=current_selected_path,
                )
            )
        elif current_selected_path.is_dir():
            current_node = self.cursor_node
            if self.cursor_node.parent and self.cursor_node.parent.data:
                current_selected_parent_path = (
                    self.cursor_node.parent.data.path
                )
            else:
                current_selected_parent_path = None
            current_selected_path = self.cursor_node.data.path
            self.post_message(
                self.DirectoryDeleteRequested(
                    node=current_node,
                    parent_path=current_selected_parent_path,
                    path=current_selected_path,
                )
            )
        event.prevent_default()

    def handle_create(self, event: Key) -> None:
        current_node = self.cursor_node
        if self.cursor_node.parent and self.cursor_node.parent.data:
            current_selected_parent_path = self.cursor_node.parent.data.path
        else:
            current_selected_parent_path = None
        current_selected_path = self.cursor_node.data.path
        if current_selected_path.is_dir():
            self.post_message(
                self.FileOrDirectoryCreateRequested(
                    node=current_node,
                    parent_path=current_selected_parent_path,
                    path=current_selected_path,
                )
            )
        event.prevent_default()

    def handle_default_bindings(self, event: Key) -> None:
        IGNORE_DEFAULT_BINDINGS = []
        if event.key in IGNORE_DEFAULT_BINDINGS:
            event.prevent_default()
        else:
            super()._on_key(event=event)

    def render_label(
        self, node: TreeNode[DirEntry], base_style: Style, style: Style
    ) -> Text:
        node_label = node._label.copy()
        node_label.stylize(style)
        if not self.is_mounted:
            return node_label

        if node._allow_expand:
            prefix = (
                '📂 ' if node.is_expanded else '📁 ',
                base_style + TOGGLE_STYLE,
            )
            node_label.stylize_before(
                self.get_component_rich_style(
                    'directory-tree--folder', partial=True
                )
            )
        else:
            FILE_ICONS_MAP = {
                'py': '🐍 ',
                'java': '☕ ',
                'html': '🌐 ',
                'css': '🎨 ',
                'tcss': '🎨 ',
                'md': '📝 ',
                'markdown': '📝 ',
                'cfg': '⚙️ ',
                'ini': '⚙️ ',
                'config': '⚙️ ',
                'yaml': '⚙️ ',
                'yml': '⚙️ ',
                'json': '⚙️ ',
                'sh': '💻 ',
                'bash': '💻 ',
                'bashrc': '💻 ',
                'zshrc': '💻 ',
                'bat': '💻 ',
                'iso': '💿 ',
                'appimage': '💿 ',
                'exe': '💿 ',
                'bin': '💿 ',
                'gitignore': '🚫 ',
                'toml': '🐭 ',
                'sql': '🗄️ ',
            }
            file_extension = ''
            if '.' in node_label.plain:
                _, file_extension = node_label.plain.lower().rsplit('.', 1)
            prefix = (FILE_ICONS_MAP.get(file_extension, '📄'), base_style)

            node_label.stylize_before(
                self.get_component_rich_style(
                    'directory-tree--file', partial=True
                ),
            )

            node_label.highlight_regex(
                r'\..+$',
                self.get_component_rich_style(
                    'directory-tree--extension', partial=True
                ),
            )

        if node_label.plain.startswith('.'):
            node_label.stylize_before(
                self.get_component_rich_style('directory-tree--hidden')
            )

        text = Text.assemble(prefix, node_label)
        return text
