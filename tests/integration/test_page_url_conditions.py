import os

import pytest
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.conditions import url, url_containing
from selene.exceptions import ConditionMismatchException
from selene.tools import visit, get_driver
from selene.tools import wait_to
from tests.integration.error_messages_test import exception_message

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


original_timeout = config.timeout


def setup_module(m):
    config.browser_name = "chrome"


def teardown_function(f):
    config.timeout = original_timeout


def test_can_wait_for_exact_url():
    visit(start_page)
    wait_to(url(get_driver().current_url))


def test_can_wait_for_part_of_url():
    visit(start_page)
    wait_to(url_containing("start_page.html"))


def test_should_wait_and_fail_for_incorrect_url():
    config.timeout = 0.1
    with pytest.raises(TimeoutException):
        visit(start_page)
        wait_to(url("xttp:/"))
