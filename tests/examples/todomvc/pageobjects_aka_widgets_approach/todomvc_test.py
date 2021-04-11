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
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selene import have, be
from selene.support.shared import browser
from tests.acceptance.helpers.todomvc import given_active


def setup_module():
    browser.set_driver(webdriver.Chrome(ChromeDriverManager().install()))


def teardown_module():
    browser.quit()


class Task:
    def __init__(self, container):
        self.container = container

    def toggle(self):
        self.container.find(".toggle").click()
        return self


class Tasks:
    def _elements(self):
        return browser.all("#todo-list>li")

    def _task_element(self, text):
        return self._elements().element_by(have.exact_text(text))

    def task(self, text):
        return Task(self._task_element(text))

    def should_be(self, *texts):
        self._elements().should(have.exact_texts(*texts))


class Footer:
    def __init__(self):
        self.container = browser.element("#footer")
        self.clear_completed = self.container.find("#clear-completed")

    def should_have_items_left(self, number_of_active_tasks):
        self.container.find("#todo-count>strong").should(
            have.exact_text(str(number_of_active_tasks))
        )


class TodoMVC:
    def __init__(self):
        self.container = browser.element("#todoapp")
        self.tasks = Tasks()
        self.footer = Footer()

    def clear_completed(self):
        self.footer.clear_completed.click()
        self.footer.clear_completed.should(be.hidden)
        return self


def test_complete_task():
    given_active("a", "b")

    page = TodoMVC()

    page.tasks.task("b").toggle()
    page.clear_completed()
    page.tasks.should_be("a")
    page.footer.should_have_items_left(1)
