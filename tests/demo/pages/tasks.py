import os

from selene import tools
from selene.bys import by_link_text
from selene.conditions import exact_text, visible, exact_texts, enabled
from selene.selene_driver import SeleneDriver
from selene.tools import get_driver

__author__ = 'yashaka'

# ---
browser = lambda: SeleneDriver(get_driver())


def s(css_selector):
    return browser().s(css_selector)


def ss(css_selector):
    return browser().ss(css_selector)
# ---


tasks = lambda: ss("#todo-list>li")


def visit():
    tools.visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html')


def filter_active():
    s(by_link_text("Active")).click()


def filter_completed():
    s(by_link_text("Completed")).click()


def add(*task_texts):
    for text in task_texts:
        s("#new-todo").assure(enabled).set_value(text).press_enter()


def toggle(task_text):
    tasks().find_by(exact_text(task_text)).find(".toggle").click()


def should_be(*task_texts):
    tasks().filter_by(visible).should_have(exact_texts(*task_texts))
