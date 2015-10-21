from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selene4 import config
from selene4.conditions import visible
from selene4.tools import visit, s
from selene4.wait import has
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

__author__ = 'ayia'


def open_todo_mvc():
    config.driver.get("file:///Users/ayia/Dropbox/Apps/Heroku/todomvc4tasj/home.html")
    WebDriverWait(config.driver, config.timeout).until(
        element_to_be_clickable((By.CSS_SELECTOR, "#new-todo")))

def execute_js(js_string):
    return config.driver.execute_script(js_string)

def given(tasks):

    if not has(s("#new-todo"), visible):
        open_todo_mvc()

    import json

    # print 'localStorage.setItem("todos-troopjs", "%s")' % (
    #     json.dumps(tasks))

    script = 'localStorage.setItem("todos-troopjs", "%s")' % (
        str(json.dumps(tasks))
        .replace('"', '\\"')
        .replace('\\\\"', '\\\\\\"')
        .replace("False", "false"))

    print script

    execute_js(script)

    open_todo_mvc()

def given_active(*taskTexts):
    return given([dict(title=text, completed=False) for text in taskTexts])

