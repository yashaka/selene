import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.wait import WebDriverWait

from selene import config
from selene.conditions import visible
from selene.tools import s, get_driver
from selene.wait import has

__author__ = 'yashaka'

# todo: refactor to not use only raw selenium helpers

TODOMVC_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html'


def open_todomvc():
    # todo: refactor to use repo copy of todomvc
    get_driver().get(TODOMVC_URL)
    WebDriverWait(get_driver(), config.timeout).until(
        element_to_be_clickable((By.CSS_SELECTOR, "#new-todo")))


def given_at_other_page():
    if not has(s("#order_details"), visible):
        get_driver().get('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/orderapp/order.html')


def execute_js(js_string):
    return get_driver().execute_script(js_string)


def given(*tasks):

    if not has(s("#new-todo"), visible):
        open_todomvc()

    import json

    script = 'localStorage.setItem("todos-troopjs", "%s")' % (
        str(json.dumps(tasks))
        .replace('"', '\\"')
        .replace('\\\\"', '\\\\\\"')
        .replace("False", "false"))

    execute_js(script)

    open_todomvc()


def given_empty_tasks():
    given()


def task(taskText, is_completed=False):
    return dict(title=taskText, completed=is_completed)


def given_active(*taskTexts):
    return given(*[task(text) for text in taskTexts])

when_active = given_active