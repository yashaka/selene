import os
from selene import config
from importlib import reload

old_timeout = config.timeout
old_polling_interval = config.poll_during_waits
old_base_url = config.base_url
old_browser_name = config.browser_name
old_browser_maximize = config.maximize_window
old_hold_browser_open = config.hold_browser_open


def setup_module(m):
    os.environ["selene_timeout"] = '3'
    os.environ["selene_poll_during_waits"] = '0.5'
    os.environ["selene_base_url"] = "http://localhost"
    os.environ["selene_browser_name"] = "chrome"
    os.environ["selene_maximize_window"] = 'True'
    os.environ['selene_hold_browser_open'] = 'True'

    reload(config)


def teardown_module(m):
    os.environ["selene_timeout"] = str(old_timeout)
    os.environ["selene_poll_during_waits"] = str(old_polling_interval)
    os.environ["selene_base_url"] = old_base_url
    os.environ["selene_browser_name"] = old_browser_name
    os.environ["selene_maximize_window"] = str(old_browser_maximize)
    os.environ['selene_hold_browser_open'] = str(old_hold_browser_open)


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
