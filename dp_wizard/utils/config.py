import os
from pathlib import Path
from typing import NamedTuple

import yaml


class _Config(NamedTuple):
    is_tutorial_mode: bool | None
    is_dark_mode: bool | None


config_root = Path(os.path.expanduser("~")) / ".dp-wizard"
if not config_root.exists():
    config_root.mkdir()  # pragma: no cover
_config_path = config_root / ".config.yaml"
_config: _Config


def _init_config():
    config_yaml = _config_path.read_text() if _config_path.exists() else ""
    config_dict = yaml.safe_load(config_yaml) or {
        "is_tutorial_mode": None,
        "is_dark_mode": None,
    }
    global _config
    _config = _Config(**config_dict)


# TODO: This is only called at application start.
# We'd like to call this when the page is reloaded, too.
# https://github.com/opendp/dp-wizard/issues/830
_init_config()


def _write_config():
    config_dict = _config._asdict()
    config_yaml = yaml.safe_dump(config_dict)
    _config_path.write_text(config_yaml)


def get_is_tutorial_mode() -> bool | None:
    return _config.is_tutorial_mode


def get_is_dark_mode() -> bool | None:
    return _config.is_dark_mode


def set_is_tutorial_mode(is_tutorial_mode: bool):
    global _config
    _config = _config._replace(is_tutorial_mode=is_tutorial_mode)
    _write_config()


def set_is_dark_mode(is_dark_mode: bool):
    global _config
    _config = _config._replace(is_dark_mode=is_dark_mode)
    _write_config()
