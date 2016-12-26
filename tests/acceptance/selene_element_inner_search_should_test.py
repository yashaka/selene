from selene.support.conditions import have

__author__ = 'yashaka'

from selenium import webdriver

from selene.tools import *
from tests.acceptance.helpers.todomvc import given_active


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_search_inner_selement():
    given_active("a", "b")
    s("#todo-list").s("li").should(have.exact_text("a"))


def test_search_inner_selene_collection():
    given_active("a", "b")
    s("#todo-list").all("li").should(have.exact_texts("a", "b"))
