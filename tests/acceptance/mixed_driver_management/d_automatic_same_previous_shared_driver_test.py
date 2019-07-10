import os

import pytest
from selenium.common.exceptions import TimeoutException

from selene import browser
from selene import config
from selene.support.conditions import be
from selene.support.conditions import have

from selene.support.jquery_style_selectors import s, ss


todomvc_url = 'https://todomvc4tasj.herokuapp.com/'
is_TodoMVC_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'

original_timeout = config.timeout


def teardown_module(m):
    config.timeout = original_timeout

#todo: enable test
def xtest_add_tasks():
    browser.open_url(todomvc_url)
    browser.should(have.js_returned_true(is_TodoMVC_loaded))

    s('#new-todo').set_value('a').press_enter()
    s('#new-todo').set_value('b').press_enter()
    s('#new-todo').set_value('c').press_enter()

    config.timeout = 0.5
    with pytest.raises(TimeoutException) as ex:
        ss("#todo-list>li").should(have.size(3))

    assert "actual: 6" in ex.value.msg
