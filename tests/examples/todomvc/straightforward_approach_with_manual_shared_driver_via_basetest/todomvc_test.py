import os

from selene import browser
from selene.support.conditions import be
from selene.support.conditions import have
from tests.base_test import *

from selene.bys import by_link_text
from selene.conditions import exact_text
from selene.support.jquery_style_selectors import s, ss

APP_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../../resources/todomvcapp/home.html'


class TestTodoMVC(BaseTest):

    def test_filter_tasks(self):
        browser.visit(APP_URL)

        s('#new-todo').should(be.enabled).set_value('a').press_enter()
        s('#new-todo').should(be.enabled).set_value('b').press_enter()
        s('#new-todo').should(be.enabled).set_value('c').press_enter()

        ss("#todo-list>li").should(have.texts('a', 'b', 'c'))

        ss("#todo-list>li").element_by(exact_text('b')).find(".toggle").click()

        s(by_link_text("Active")).click()
        ss("#todo-list>li").filtered_by(be.visible).should(have.texts('a', 'c'))

        s(by_link_text("Completed")).click()
        ss("#todo-list>li").filtered_by(be.visible).should(have.texts('b'))


