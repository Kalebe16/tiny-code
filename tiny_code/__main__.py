from pathlib import Path

from rich.console import Console
from rich.panel import Panel
import sys


def before_run_app() -> None:
    def adjust_python_path() -> None:
        """
        Prepares the environment for running the app with `textual run --dev`
        """
        MODULE_PARENT_PATH = Path(__file__).parent.parent
        if str(MODULE_PARENT_PATH) not in sys.path:
            sys.path.append(str(MODULE_PARENT_PATH))

    def monkey_patch() -> None:
        from tiny_code.monkey_patch import monkey_patch_pathlib

        monkey_patch_pathlib()

    adjust_python_path()
    monkey_patch()


def run_app() -> None:
    from tiny_code.app import TinyCodeApp

    console = Console()

    if len(sys.argv) < 2:
        console.print(
            Panel(
                '[bold red]You must provide a directory path. Use: `tiny-code .`[/]',
                title='ERROR',
                border_style='bold red',
            )
        )
        return

    dir_path = Path(sys.argv[1]).resolve()
    if not dir_path.is_dir():
        console.print(
            Panel(
                f'[bold red]`{dir_path}` not exists or is not a valid directory path[/]',
                title='ERROR',
                border_style='bold red',
            )
        )
        return

    tiny_code_app = TinyCodeApp(dir_path=dir_path)
    tiny_code_app.run()


if __name__ == '__main__':
    before_run_app()
    run_app()
