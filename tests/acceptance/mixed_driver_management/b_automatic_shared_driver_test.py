import os

from selene.support.conditions import be
from selene.support.conditions import have

from selene import browser
from selene.support.jquery_style_selectors import s, ss


todomvc_url = 'https://todomvc4tasj.herokuapp.com/'
is_TodoMVC_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'


def test_add_tasks():
    browser.open_url(todomvc_url)
    browser.should(have.js_returned_true(is_TodoMVC_loaded))

    s('#new-todo').set_value('a').press_enter()
    s('#new-todo').set_value('b').press_enter()
    s('#new-todo').set_value('c').press_enter()

    ss("#todo-list>li").should(have.texts('a', 'b', 'c'))