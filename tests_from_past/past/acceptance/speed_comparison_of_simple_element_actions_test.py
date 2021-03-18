# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selene.api.past import visible
from selene.api.past import set_driver, driver, open_url
from selene.support.jquery_style_selectors import s
from tests_from_past.past.acceptance import get_test_driver
from tests.helpers import time_spent
from tests_from_past.past.acceptance import TODOMVC_URL

browser = None
shaded_browser = None


def setup_function(f):
    global browser
    global shaded_browser

    set_driver(get_test_driver())
    open_url(TODOMVC_URL)
    s("#new-todo").should_be(visible)

    browser = get_test_driver()
    browser.get(TODOMVC_URL)
    WebDriverWait(browser, 4).until(
        expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#new-todo")
        )
    )

    shaded_browser = get_test_driver()


def teardown_function(f):
    global browser
    global shaded_browser
    browser.quit()
    driver().quit()
    shaded_browser.quit()


def create_tasks_with_raw_selenium():
    global browser
    new_todo = browser.find_element_by_css_selector("#new-todo")
    for task_text in map(str, range(10)):
        new_todo.send_keys(task_text + Keys.ENTER)


def create_tasks_with_selenium_with_research():
    global browser
    for task_text in map(str, range(10)):
        new_todo = browser.find_element_by_css_selector("#new-todo")
        new_todo.send_keys(task_text + Keys.ENTER)


def create_tasks_with_selene_and_send_keys():
    for task_text in map(str, range(10)):
        s("#new-todo").send_keys(task_text + Keys.ENTER)


def create_tasks_with_selene_with_cash():
    new_todo = s("#new-todo").caching()
    for task_text in map(str, range(10)):
        new_todo.send_keys(task_text + Keys.ENTER)


# todo: review these tests

# def test_selene_is_almost_as_fast_selenium_with_research_and_initial_wait_for_visibility():
#     selene_time = time_spent(create_tasks_with_selene_and_send_keys)
#     selenium_time = time_spent(create_tasks_with_selenium_with_research)
#     # print("%s vs %s" % (selene_time, selenium_time))
#     assert selene_time < 1.75 * selenium_time
#     # assert selene_time < 1.12 * selenium_time


def x_test_selene_is_from_32_to_75_percents_slower_than_raw_selenium():
    selene_time = time_spent(create_tasks_with_selene_and_send_keys)
    selenium_time = time_spent(create_tasks_with_raw_selenium)
    # print("%s vs %s" % (selene_time, selenium_time))
    assert selene_time <= 1.75 * selenium_time


# def test_cashed_selene_is_almost_as_fast_raw_selenium():
#     selene_time = time_spent(create_tasks_with_selene_with_cash)
#     selenium_time = time_spent(create_tasks_with_raw_selenium)
#     # print("%s vs %s" % (selene_time, selenium_time))
#     assert selene_time < 1.15 * selenium_time
#     # assert selene_time < 1.12 * selenium_time
