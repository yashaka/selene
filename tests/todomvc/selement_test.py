__author__ = 'ayia'

from selenium import webdriver

from selene.conditions import *
from selene.tools import *
from tests.todomvc.helpers.todomvc import given_active, given_at_other_page


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_assure_hidden():
    given_active("a")
    s("#clear-completed").assure(hidden)


def test_assure_absent():
    given_at_other_page()
    s("#new-todo").assure_not(exist)
