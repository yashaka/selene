import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene.conditions import visible
from selene.tools import *

# todo: find a way to work with config in "scope", like in "context_manager" style
current_wait_time = config.timeout


def setup_module():
    set_driver(webdriver.Firefox())
    config.timeout = 0.1


def teardown_module():
    config.timeout = current_wait_time
    get_driver().quit()


def test_it_fails_to_assure_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").assure(visible)


def test_it_fails_to_set_value_of_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").set_value("this text will not be set")

# todo: increase coverage