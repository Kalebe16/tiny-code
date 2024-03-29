from dataclasses import asdict, dataclass


@dataclass
class Config:
    dark_mode: bool
    show_line_numbers: bool
    break_lines: bool
    theme: str
    tab_size: int

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
