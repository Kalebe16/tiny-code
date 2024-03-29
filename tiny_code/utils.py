from math import ceil, floor
from pathlib import Path
from typing import Literal, Union


def find_first_char_non_void(string: str) -> int:
    return len(string) - len(string.lstrip())


def find_last_char_non_void(string: str) -> int:
    return len(string.rstrip())


def is_multiple_of(multiple_of: int, number: int) -> bool:
    return number % multiple_of == 0


def closest_multiple_of(
    multiple_of: int,
    number: int,
    round_direction: Literal['up', 'down'],
) -> int:
    if multiple_of == 0:
        raise ValueError('The value zero from `multiple_of` is not permited')

    if round_direction == 'up':
        return ceil(number / multiple_of) * multiple_of
    elif round_direction == 'down':
        return floor(number / multiple_of) * multiple_of


def tab_text(
    text: str, action: Literal['tab', 'shift+tab'], tab_size: int = 4
) -> str:
    lines = text.split('\n')
    updated_lines = []

    for line in lines:
        if action == 'tab':
            first_non_space_index = find_first_char_non_void(line)
            spaces_to_add = tab_size - (first_non_space_index % tab_size)
            updated_lines.append((' ' * spaces_to_add) + line)
        elif action == 'shift+tab':
            first_non_space_index = find_first_char_non_void(line)
            spaces_to_remove = min(
                first_non_space_index,
                first_non_space_index % tab_size or tab_size,
            )
            updated_lines.append(line[spaces_to_remove:])

    return '\n'.join(updated_lines)


def comment_or_uncomment_text(text: str, comment_char: str) -> str:
    lines = text.split('\n')
    updated_lines = []

    for line in lines:
        if line.strip() == '':
            updated_lines.append(line.strip())
            continue

        index_first_char = find_first_char_non_void(line)
        first_char = line[index_first_char]
        # Uncomment line
        if first_char == comment_char:
            updated_line = (
                line[:index_first_char] + line[index_first_char + 1 :].lstrip()
            )
            updated_lines.append(updated_line)
        # Comment line
        elif first_char != comment_char:
            updated_line = (
                line[:index_first_char]
                + comment_char
                + ' '
                + line[index_first_char:]
            )
            updated_lines.append(updated_line)

    return '\n'.join(updated_lines)


def remove_dir_or_file(dir_or_file_path: Union[Path, str]) -> None:
    dir_or_file_path = Path(dir_or_file_path)
    if not dir_or_file_path.exists():
        return
    if dir_or_file_path.is_dir():
        clear_dir(dir_path=dir_or_file_path)
        dir_or_file_path.rmdir()
    elif dir_or_file_path.is_file():
        dir_or_file_path.unlink()


def clear_dir(dir_path: Union[Path, str]) -> None:
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        return

    dir_content = dir_path.rglob('*', True)

    for path in dir_content:
        if path.is_file():
            path.unlink()

    for path in dir_content:
        if path.is_dir():
            path.rmdir()
