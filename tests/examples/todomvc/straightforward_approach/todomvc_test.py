# coding=utf-8
from selene import browser
from selene import config
from selene.support.conditions import be
from selene.support.conditions import have

from selene.bys import by_link_text
from selene.conditions import exact_text
from selene.support.jquery_style_selectors import s, ss


class TestTodoMVC(object):

    def test_filter_tasks(self):
        browser.open_url('https://todomvc4tasj.herokuapp.com/')
        clear_completed_js_loaded = "return $._data($('#clear-completed').get(0), 'events').hasOwnProperty('click')"
        browser.wait_to(have.js_returned_true(clear_completed_js_loaded), timeout=config.timeout*3)
        browser.wait_to(have.title(u'TroopJS • TodoMVC'))

        s('#new-todo').should(be.enabled).set_value('a').press_enter()
        s('#new-todo').should(be.enabled).set_value('b').press_enter()
        s('#new-todo').should(be.enabled).set_value('c').press_enter()

        ss("#todo-list>li").should(have.texts('a', 'b', 'c'))

        ss("#todo-list>li").element_by(exact_text('b')).find(".toggle").click()

        s(by_link_text("Active")).click()
        ss("#todo-list>li").filtered_by(be.visible).should(have.texts('a', 'c'))

        s(by_link_text("Completed")).click()
        ss("#todo-list>li").filtered_by(be.visible).should(have.texts('b'))


