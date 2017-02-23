import os

import pytest
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.support.conditions import be
from selene.support.conditions import have

from selene.browser import ss, s, visit

original_timeout = config.timeout


def teardown_module(m):
    config.timeout = original_timeout


def test_filter_tasks():
    visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html')

    s('#new-todo').should(be.enabled).set_value('a').press_enter()
    s('#new-todo').should(be.enabled).set_value('b').press_enter()
    s('#new-todo').should(be.enabled).set_value('c').press_enter()

    config.timeout = 0.5
    with pytest.raises(TimeoutException) as ex:
        ss("#todo-list>li").should(have.size(3))

    assert "actual: 6" in ex.value.msg
