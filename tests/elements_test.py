import os

import pytest
from selenium.webdriver.common.by import By

from selene import config
from selene import visit, s, ss
from selene.waits import ExpiredWaitingException


def setup_module():
    config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/resources/testapp/'
    config.default_wait_time = 0.1
    visit('elements.html')


def test_find_element_by_css_for_not_existent_locator():
    with pytest.raises(ExpiredWaitingException):
        s("#i-do-not-exist").insist()


def test_find_element_by_css_for_existent_locator():
    s('.css').insist()


def test_find_element_by_id():
    s('item_31', By.ID).insist()


def test_find_element_by_xpath():
    s('//input[@id="item_31"]', By.XPATH).insist()


def test_find_element_by_name():
    s('last_name', By.NAME).insist()


def test_find_elements_by_css():
    ss('.item').insist(lambda e: len(e) == 5)


def test_find_elements_by_xpath():
    ss('//li', By.XPATH).insist(lambda e: len(e) == 5)


def test_is_visible_for_hidden_locator():
    assert not s('h', By.ID).is_visible()


def test_is_visible_for_visible_locator():
    assert s('.css').is_visible()


def test_is_present_for_not_existent_locator():
    assert not s('.dddh').is_present()


def test_is_present_for_existent_locator():
    assert s('.css').is_present()


def test_has_text_for_not_populated_locator():
    assert not s('.css').has_text()


def test_has_test_for_populated_locator():
    assert s('ol > li').has_text()


def test_is_empty_for_filled_collection_of_elements():
    assert not ss('ol').is_empty()
