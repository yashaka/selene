import os

from selene.conditions import css_class, texts, text, size, hidden, empty
from selene.tools import *
from tests.base_test import *


class TestTodoMVC(BaseTest):

    def test_selene_demo(self):
        tasks = ss("#todo-list>li")
        active_tasks = tasks.filtered_by(css_class("active"))

        visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/todomvcapp/home.html')

        for task_text in ["1", "2", "3"]:
            s("#new-todo").set_value(task_text).press_enter()

        tasks.assure(texts("1", "2", "3")).should_each(css_class("active"))
        s("#todo-count").assure(text("3"))

        tasks[2].s(".toggle").click()

        active_tasks.assure(texts("1", "2"))
        active_tasks.assure(size(2))

        tasks.filtered_by(css_class("completed")).assure(texts("3"))

        s("a[href='#/active']").click()
        tasks[:2].assure(texts("1", "2"))
        tasks[2].assure(hidden)

        s("#toggle-all").click()
        s("#clear-completed").click()
        tasks.assure(empty)

