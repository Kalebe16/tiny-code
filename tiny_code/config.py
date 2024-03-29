import json

from tiny_code.consts import JSON_CONFIG_PATH
from tiny_code.entities import Config


class ConfigManager:
    @classmethod
    def get(cls) -> Config:
        current_config = json.loads(
            JSON_CONFIG_PATH.read_text(encoding='utf-8')
        )
        return Config(
            dark_mode=current_config.get('dark_mode'),
            show_line_numbers=current_config.get('show_line_numbers'),
            break_lines=current_config.get('break_lines'),
            theme=current_config.get('theme'),
            tab_size=current_config.get('tab_size'),
        )

    @classmethod
    def set(cls, config: Config) -> None:
        JSON_CONFIG_PATH.write_text(
            data=json.dumps(config.to_dict(), indent=2), encoding='utf-8'
        )
