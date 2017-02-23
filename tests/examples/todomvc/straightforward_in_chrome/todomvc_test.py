from selene import config
from selene.support import by
from selene.support.conditions import be
from selene.support.conditions import have
from selene.browser import visit, s, ss, wait_to


def test_filter_tasks():
    config.browser_name = 'chrome'

    visit('https://todomvc4tasj.herokuapp.com')
    wait_to(have.js_returned_true("return $._data($('#clear-completed').get(0), 'events').hasOwnProperty('click')"), timeout=8)

    s('#new-todo').set_value('a').press_enter()
    s('#new-todo').set_value('b').press_enter()
    s('#new-todo').set_value('c').press_enter()
    ss('#todo-list li').should(have.exact_texts('a', 'b', 'c'))

    ss('#todo-list li').element_by(have.exact_text('b')).element('.toggle').click()
    s(by.link_text('Active')).click()
    ss('#todo-list li').filtered_by(be.visible).should(have.exact_texts('a', 'c'))

    s(by.link_text('Completed')).click()
    ss('#todo-list li').filtered_by(be.visible).should(have.exact_texts('b'))

    s(by.link_text('All')).click()
    ss('#todo-list li').filtered_by(be.visible).should(have.exact_texts('a', 'b', 'c'))

