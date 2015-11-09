import pytest
from stopit import TimeoutException

from selene import *
from selene.conditions import visible

# todo: find a way to work with config in "scope", like in "context_manager" style
current_wait_time = config.default_wait_time


def setup_module():
    config.default_wait_time = 1


def teardown_module():
    config.default_wait_time = current_wait_time


def test_it_fails_insist_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").insist(visible)


def test_it_fails_set_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").set("this text will not be set")

# todo: increase coverage