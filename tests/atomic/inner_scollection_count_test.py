from selenium import webdriver

from selene import config
from selene.selene_driver import SeleneDriver
from tests.atomic.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = SeleneDriver(webdriver.Firefox())
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


def teardown_module(m):
    driver.quit()


def test_counts_invisible_tasks():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear' style='display:none'>Kate</li>
                   </ul>''')
    assert len(elements) == 2
