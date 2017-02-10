import os

import pytest
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.conditions import exact_url, partial_url
from selene.exceptions import ConditionMismatchException
from selene.tools import visit, get_driver
from selene.tools import wait_to
from tests.integration.error_messages_test import exception_message

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"


def test_can_wait_for_exact_url():
    visit(start_page)
    wait_to(exact_url(get_driver().current_url))


def test_can_wait_for_part_of_url():
    visit(start_page)
    wait_to(partial_url("start_page.html"))


def test_should_wait_and_fail_for_incorrect_url():
    with pytest.raises(TimeoutException):
        visit(start_page)
        wait_to(exact_url("xttp:/"))
