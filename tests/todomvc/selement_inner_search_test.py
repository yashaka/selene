__author__ = 'yashaka'

from selenium import webdriver

from selene.tools import *
from tests.todomvc.helpers.todomvc import given_active


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_search_inner_selement():
    given_active("a", "b")
    s("#todo-list").s("li").assure(exact_text("a"))


def test_search_inner_selements_collection():
    given_active("a", "b")
    s("#todo-list").ss("li").assure(exact_texts("a", "b"))
