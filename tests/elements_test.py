import os

from selenium.webdriver.common.by import By

from selene import config
from selene import visit, s, ss


def setup_module():
    config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/resources/testapp/'


def test_find_element_by_css():
    visit('elements.html')
    s('.css').insist()


def test_find_element_by_id():
    visit('elements.html')
    s('item_31', By.ID).insist()


def test_find_element_by_xpath():
    visit('elements.html')
    s('//input[@id="item_31"]', By.XPATH).insist()


def test_find_element_by_name():
    visit('elements.html')
    s('last_name', By.NAME).insist()


def test_find_elements_by_css():
    visit('elements.html')
    ss('.item').insist(lambda e: len(e) == 5)


def test_find_elements_by_xpath():
    visit('elements.html')
    ss('//li', By.XPATH).insist(lambda e: len(e) == 5)
