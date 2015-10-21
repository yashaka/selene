from selenium.common.exceptions import TimeoutException
from selene4.conditions import *
from selene4.tools import *
from selene4.wait import wait_for
from tests.todomvc.todomvc_helpers import given, given_active
from selenium import webdriver
import time
import pytest


def setup_function(fn):
    config.driver = webdriver.Firefox()

def teardown_function(fn):
    config.driver.quit()


def test_assure_passes():
    given_active("a", "b")
    ss("#todo-list>li").assure(exact_texts("a", "b"))


def test_assure_fails():
    given_active("a", "b")
    with pytest.raises(TimeoutException):
        ss("#todo-list>li").assure(exact_texts("a.", "b."), timeout=0.1)









