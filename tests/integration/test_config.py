import os

from selene.environment import *

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

from selene import config

old_timeout = config.timeout
old_polling_interval = config.poll_during_waits
old_base_url = config.base_url
old_browser_name = config.browser_name
old_browser_maximize = config.start_maximized
old_hold_browser_open = config.hold_browser_open


def setup_module(m):
    os.environ[SELENE_TIMEOUT] = '3'
    os.environ[SELENE_POLL_DURING_WAITS] = '0.5'
    os.environ[SELENE_BASE_URL] = "http://localhost"
    os.environ[SELENE_BROWSER_NAME] = "chrome"
    os.environ[SELENE_START_MAXIMIZED] = 'True'
    os.environ[SELENE_HOLD_BROWSER_OPEN] = 'True'

    reload(config)


def teardown_module(m):
    os.environ[SELENE_TIMEOUT] = str(old_timeout)
    os.environ[SELENE_POLL_DURING_WAITS] = str(old_polling_interval)
    os.environ[SELENE_BASE_URL] = old_base_url
    os.environ[SELENE_BROWSER_NAME] = old_browser_name
    os.environ[SELENE_START_MAXIMIZED] = str(old_browser_maximize)
    os.environ[SELENE_HOLD_BROWSER_OPEN] = str(old_hold_browser_open)


def test_timeout():
    assert config.timeout == 3


def test_pooling_wait():
    assert config.poll_during_waits == 0.5


def test_base_url():
    assert config.base_url == "http://localhost"


def test_browser_name():
    assert config.browser_name == "chrome"


def test_browser_maximize():
    assert config.start_maximized is True


def test_hold_browser_open():
    assert config.hold_browser_open is True
