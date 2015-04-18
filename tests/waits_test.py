import pytest
from stopit import TimeoutException
from selene.conditions import visible
from selene.tools import *

config.default_wait_time = 1


def test_it_fails_insist_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").insist(visible)


def test_it_fails_set_not_existent_element():
    with pytest.raises(TimeoutException):
        s("#i-do-not-exist").set("this text will not be set")

# todo: increase coverage