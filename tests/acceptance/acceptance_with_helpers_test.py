from selenium.webdriver.common.keys import Keys

from selene.conditions import visible, empty, exact_text, css_class
from selene.support.conditions import be
from selene.support.conditions import have
from selene.support.jquery_style_selectors import s, ss

__author__ = 'yashaka'

from selene.browser import *


class TestTodoMVC(object):

    def test_tasks_life_cycle(self):

        visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/todomvcapp/home.html')

        add("a")

        edit("a", "a edited")

        # complete
        toggle("a edited")
        filter_active()
        tasks.filtered_by(visible).assure(empty)

        # create from active filter
        add("b")
        toggle("b")
        filter_completed()
        assert_visible_tasks("a edited", "b")

        # reopen from completed filter
        toggle("a edited")
        assert_visible_tasks("b")
        filter_active()
        assert_visible_tasks("a edited")
        filter_all()
        assert_tasks("a edited", "b")

        # clear completed
        clear_completed()
        assert_tasks("a edited")

        # complete all
        toggle_all()
        filter_active()
        tasks.filtered_by(visible).assure(empty)

        # reopen all
        toggle_all()
        assert_visible_tasks("a edited")

        add("c")

        # delete by editing to ''
        edit("a edited", "")
        filter_all()
        assert_tasks("c")

        # delete
        delete("c")
        tasks.assure(empty)


tasks = ss("#todo-list>li")


def add(*taskTexts):
    for text in taskTexts:
        s("#new-todo").should(be.enabled).send_keys(text, Keys.ENTER)


def assert_tasks(*task_texts):
    tasks.should(have.exact_texts(*task_texts))


def assert_visible_tasks(*task_texts):
    tasks.filtered_by(visible).should(have.texts(*task_texts))


def assert_no_visible_tasks():
    tasks.filtered_by(visible).should(be.empty)


def assert_no_tasks():
    tasks.assure(empty)


def edit(old_task_name, new_task_name):
    tasks.element_by(exact_text(old_task_name)).double_click()
    tasks.element_by(css_class("editing")).element(".edit").set_value(new_task_name).press_enter()
    # compare:
    # tasks.s(exact_text(old_task_name)).s("label").double_click()
    # tasks.s(css_class("editing")).s(".edit").set_value(new_task_name).press_enter()


def toggle(task_name):
    tasks.element_by(exact_text(task_name)).element(".toggle").click()


def delete(task_name):
    tasks.element_by(exact_text(task_name)).hover().element(".destroy").click()
    # todo: here, after hover() - it's more convenient to use find over element... should we then make find non-lazy?


def toggle_all():
    s("#toggle-all").click()


def clear_completed():
    s("#clear-completed").click()


def filter_all():
    s("[href='#/']").click()


def filter_active():
    s("[href*='active']").click()


def filter_completed():
    s("[href*='completed']").click()
