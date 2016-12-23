from selene.conditions import css_class
from tests.atomic.helpers.givenpage import GivenPage
from selenium import webdriver
from selene.tools import *

__author__ = 'yashaka'

driver = webdriver.Firefox()
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE


def setup_module(m):
    set_driver(driver)


def teardown_module(m):
    get_driver().quit()


def test_counts_invisible_tasks():
    GIVEN_PAGE.opened_empty()
    elements = ss('li').filterBy(css_class('will-appear'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li>Anonymous</li>
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear' style='display:none'>Kate</li>
                   </ul>''')
    assert len(elements) == 2
