import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selene import config
from selene.conditions import visible
from selene.tools import visit, s, get_driver
from selene.wait import has
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

__author__ = 'ayia'

# todo: refactor to not use only raw selenium helpers

def open_todomvc():
    # todo: refactor to use repo copy of todomvc
    get_driver().get('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html')
    WebDriverWait(get_driver(), config.timeout).until(
        element_to_be_clickable((By.CSS_SELECTOR, "#new-todo")))

def given_at_other_page():
    if not has(s("#order_details"), visible):
        get_driver().get('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/orderapp/order.html')

def execute_js(js_string):
    return get_driver().execute_script(js_string)

def given(tasks):

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

def given_active(*taskTexts):
    return given([dict(title=text, completed=False) for text in taskTexts])

when_active = given_active