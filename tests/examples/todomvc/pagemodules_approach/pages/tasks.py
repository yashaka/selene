import os

from selene import tools
from selene.bys import by_link_text
from selene.conditions import exact_text, visible, exact_texts, enabled
from selene.support.conditions import have
from selene.tools import ss, s, wait_to

__author__ = 'yashaka'


_elements = ss("#todo-list>li")


def visit():
    tools.visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../../../resources/todomvcapp/home.html')
    wait_to(have.js_returned_true("return $._data($('#clear-completed').get(0), 'events').hasOwnProperty('click')"))


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