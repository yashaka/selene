import os

os.environ["selene_timeout"] = "3"
os.environ["selene_poll_during_waits"] = "0.5"
os.environ["selene_base_url"] = "http://localhost"
os.environ["selene_browser_name"] = "chrome"
os.environ["selene_maximize_window"] = "True"
os.environ['selene_hold_browser_open'] = "True"

from selene import config
from importlib import reload


def setup_module(m):
    reload(config)


def test_timeout():
    assert config.timeout == 3


def test_pooling_wait():
    assert config.poll_during_waits == 0.5


def test_base_url():
    assert config.base_url == "http://localhost"


def test_browser_name():
    assert config.browser_name == "chrome"


def test_browser_maximize():
    assert config.maximize_window is True


def test_hold_browser_open():
    assert config.hold_browser_open is True
