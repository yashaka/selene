import os

from selenium import webdriver

from selene.support.conditions import be
from selene.support.conditions import have
from selene.tools import set_driver, get_driver, visit, s, ss


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_filter_tasks():
    visit('file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html')

    s('#new-todo').should(be.enabled).set_value('a').press_enter()
    s('#new-todo').should(be.enabled).set_value('b').press_enter()
    s('#new-todo').should(be.enabled).set_value('c').press_enter()

    ss("#todo-list>li").should(have.texts('a', 'b', 'c'))
