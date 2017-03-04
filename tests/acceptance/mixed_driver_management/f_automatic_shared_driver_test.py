import os

from selene import browser
from selene.support.conditions import be
from selene.support.conditions import have

from selene.support.jquery_style_selectors import s, ss


def test_filter_tasks():
    browser.open_url('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html')

    s('#new-todo').should(be.enabled).set_value('a').press_enter()
    s('#new-todo').should(be.enabled).set_value('b').press_enter()
    s('#new-todo').should(be.enabled).set_value('c').press_enter()

    ss("#todo-list>li").should(have.texts('a', 'b', 'c'))