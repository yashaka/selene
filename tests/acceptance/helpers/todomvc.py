import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.wait import WebDriverWait

from selene import config
from selene.conditions import visible
from selene.browser import driver
from selene.support.jquery_style_selectors import s
from selene.wait import satisfied

__author__ = 'yashaka'

# todo: refactor to not use only raw selenium helpers

# TODOMVC_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html'
TODOMVC_URL = 'https://todomvc4tasj.herokuapp.com/'
OTHER_PAGE_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/orderapp/order.html'
is_TodoMVC_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'


class js_returned_true(object):
    def __init__(self, script):
        self.script = script

    def __call__(self, driver):
        result = driver.execute_script(self.script)
        if not result:
            return False
        else:
            return driver


def open_todomvc():
    # todo: refactor to use repo copy of todomvc
    driver().get(TODOMVC_URL)
    WebDriverWait(driver(), config.timeout).until(
        js_returned_true(is_TodoMVC_loaded))


def given_at_other_page():
    if not satisfied(s("#order_details"), visible):
        driver().get(OTHER_PAGE_URL)


def execute_js(js_string):
    return driver().execute_script(js_string)


def given(*tasks):

    if not satisfied(s("#new-todo"), visible):
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