from pathlib import Path

import pytest


@pytest.fixture
def config():
    test_config_path = Path(__file__).parent.parent / "fixtures/.test_config.yaml"
    assert not test_config_path.exists()
    from dp_wizard.utils import config

    config._config_path = test_config_path
    config._init_config()
    yield config
    test_config_path.unlink()


def test_config(config):
    assert config.get_is_dark_mode() is None
    assert config.get_is_tutorial_mode() is None

    config.set_is_dark_mode(True)
    assert config.get_is_dark_mode()

    config.set_is_tutorial_mode(True)
    assert config.get_is_tutorial_mode()

    config.set_is_dark_mode(False)
    assert not config.get_is_dark_mode()

    config.set_is_tutorial_mode(False)
    assert not config.get_is_tutorial_mode()
