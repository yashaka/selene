from selene import browser
from selene.conditions import exact_text, hidden, exact_texts
from selene.support.jquery_style_selectors import s, ss

from tests.acceptance.helpers.helper import get_test_driver
from tests.acceptance.helpers.todomvc import given_active


def setup_module(m):
    browser.set_driver(get_test_driver())


def teardown_module(m):
    browser.driver().quit()


class Task(object):
    def __init__(self, container):
        self.container = container

    def toggle(self):
        self.container.find(".toggle").click()
        return self


class Tasks(object):
    def _elements(self):
        return ss("#todo-list>li")

    def _task_element(self, text):
        return self._elements().element_by(exact_text(text))

    def task(self, text):
        return Task(self._task_element(text))

    def should_be(self, *texts):
        self._elements().should_have(exact_texts(*texts))


class Footer(object):
    def __init__(self):
        self.container = s("#footer")
        self.clear_completed = self.container.find("#clear-completed")

    def should_have_items_left(self, number_of_active_tasks):
        self.container.find("#todo-count>strong").should_have(exact_text(str(number_of_active_tasks)))


class TodoMVC(object):
    def __init__(self):
        self.container = s("#todoapp")
        self.tasks = Tasks()
        self.footer = Footer()

    def clear_completed(self):
        self.footer.clear_completed.click()
        self.footer.clear_completed.should_be(hidden)
        return self


def test_complete_task():
    given_active("a", "b")

    page = TodoMVC()

    page.tasks.task("b").toggle()
    page.clear_completed()
    page.tasks.should_be("a")
    page.footer.should_have_items_left(1)
