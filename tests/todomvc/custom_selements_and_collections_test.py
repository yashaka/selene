__author__ = 'ayia'

from selenium import webdriver

from selene.conditions import *
from selene.tools import *
from tests.todomvc.helpers.todomvc import given_active


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


class Task(SElement):
    def delete(self):
        self.hover()
        self.s(".destroy").click()


def test_custom_selement():
    given_active("a", "b")
    Task("#todo-list>li:nth-child(1)").delete()
    ss("#todo-list>li").assure(texts("b"))


def test_selements_collections_of_custom_selements():
    given_active("a", "b", "c")
    ss("#todo-list>li").of(Task)[1].delete()
    ss("#todo-list>li").of(Task).assure(texts("a", "c"))

    ss("#todo-list>li").of(Task).find(text("c")).delete()
    ss("#todo-list>li").of(Task).assure(texts("a"))


class TodoMVC(SElement):
    def init(self):
        self.tasks = ss("#todo-list>li").of(self.Task)
        self.footer = self.Footer("#footer")
        # self.footer = s("#footer").of(self.Footer) # todo: add such syntax

    def clear_completed(self):
        self.footer.clear_completed.click()
        self.footer.clear_completed.assure(hidden)
        return self

    class Task(SElement):
        def toggle(self):
            self.s(".toggle").click()
            return self

    class Footer(SElement):
        def init(self):
            self.clear_completed = self.s("#clear-completed")

        def assure_items_left(self, number_of_active_tasks):
            self.s("#todo-count>strong").assure(exact_text(str(number_of_active_tasks)))


def test_nested_custom_selements():
    given_active("a", "b")

    page = TodoMVC("#todoapp") # it's more widget than page... todo: rename to todomvc, etc...

    page.tasks.find(text("b")).toggle()
    page.clear_completed()
    page.tasks.assure(texts("a"))
    page.footer.assure_items_left(1)

