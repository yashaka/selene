__author__ = 'ayia'

from selenium.common.exceptions import TimeoutException
from selene4.conditions import *
from selene4.tools import *
from selene4.wait import wait_for
from tests.todomvc.todomvc_helpers import given, given_active
from selenium import webdriver
import time
import pytest
from selene4.bys import *

config.driver = webdriver.Firefox()

def find_element(locator):
    return config.driver.find_element(*locator)

def teardown_module(m):
    config.driver.quit()


def test_by_text_with_single_and_double_quotes():
    given_active("""Fred's last name is "Li".""")
    assert find_element(by_text("""Fred's last name is "Li".""")).is_displayed()

