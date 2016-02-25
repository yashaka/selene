__author__ = 'ayia'

from selenium import webdriver

from selene.conditions import *
from selene.tools import *
from tests.todomvc.helpers.todomvc import given_active, given_at_other_page


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_assure_and_alias_methods():
    given_active("a")
    s("#clear-completed").assure(hidden)
    s("#clear-completed").insist(hidden)  # alias
    s("#clear-completed").should(hidden)  # alias
    s("#clear-completed").should_be(hidden)  # alias
    s("#clear-completed").should_have(hidden)  # alias


def test_assure_not_and_alias_methods():
    given_at_other_page()
    s("#new-todo").assure_not(exist)
    s("#new-todo").insist_not(exist)  # alias
    s("#new-todo").should_not(exist)  # alias
    s("#new-todo").should_not_be(exist)  # alias
    s("#new-todo").should_not_have(exist)  # alias


def test_lazy_inner_s():
    given_at_other_page()
    s("#todo-list>li:nth-of-type(1)").s(".toggle")
    s("#todo-list>li:nth-of-type(1)").find(".toggle")  # alias


def test_lazy_inner_ss():
    given_at_other_page()
    s("#todo-list").ss("li")
    s("#todo-list").find_all("li")  # alias
