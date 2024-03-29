from pathlib import Path
import os


def monkey_patch_pathlib() -> None:
    def is_readable(self: Path) -> bool:
        return os.access(self, os.R_OK)

    def is_writable(self: Path) -> bool:
        return os.access(self, os.W_OK)

    def is_executable(self: Path) -> bool:
        return os.access(self, os.X_OK)

    Path.is_readable = is_readable
    Path.is_writable = is_writable
    Path.is_executable = is_executable
