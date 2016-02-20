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
    s("#clear-completed").insist(hidden)
    s("#clear-completed").should(hidden)
    s("#clear-completed").should_be(hidden)
    s("#clear-completed").should_have(hidden)


def test_assure_not_and_alias_methods():
    given_at_other_page()
    s("#new-todo").assure_not(exist)
    s("#new-todo").insist_not(exist)
    s("#new-todo").should_not(exist)
    s("#new-todo").should_not_be(exist)
    s("#new-todo").should_not_have(exist)
