from selene.bys import by_link_text
from selene.api.past import exact_text, visible, exact_texts, enabled
from selene.support.conditions import have
from selene.api.past import browser
from selene.support.jquery_style_selectors import s, ss

__author__ = 'yashaka'


_elements = ss("#todo-list>li")

app_url = 'https://todomvc4tasj.herokuapp.com/'

def visit():
    browser.open_url(app_url)
    clear_completed_js_loaded = "return $._data($('#clear-completed').get(0), 'events').hasOwnProperty('click')"
    browser.wait_to(have.js_returned_true(clear_completed_js_loaded))


def filter_active():
    s(by_link_text("Active")).click()


def filter_completed():
    s(by_link_text("Completed")).click()


def add(*task_texts):
    for text in task_texts:
        s("#new-todo").assure(enabled).set_value(text).press_enter()


def toggle(task_text):
    _elements.element_by(exact_text(task_text)).find(".toggle").click()


def should_be(*task_texts):
    _elements.filtered_by(visible).should_have(exact_texts(*task_texts))


def clear_completed():
    s('#clear-completed').click()