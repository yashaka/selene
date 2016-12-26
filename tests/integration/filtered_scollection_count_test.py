from selenium import webdriver

from selene import config
from selene.selene_driver import SeleneDriver
from selene.support.conditions import have
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = SeleneDriver.wrap(webdriver.Firefox())
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


def teardown_module(m):
    driver.quit()


def test_counts_invisible_tasks():
    GIVEN_PAGE.opened_empty()
    elements = driver.all('li').filtered_by(have.css_class('will-appear'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li>Anonymous</li>
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear' style='display:none'>Kate</li>
                   </ul>''')
    assert len(elements) == 2
