"""
    This file contains the full configuration options for the python package.

    Settings can be obtained and modified with the following method:
        settings = from package_name.config.settings import get_settings
        settings = get_settings()
        settings.example = 5
"""


from dataclasses import dataclass, field

@dataclass
class Settings:
    example: int = field(
        default=0,
        metadata={"description": "Here the description"}
    )
    


_settings = Settings()


def get_settings() -> Settings:
    return _settings

def reset_settings():
    global _settings
    _settings = Settings()
