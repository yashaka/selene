import os

import pytest
from selenium.common.exceptions import TimeoutException

import selene
from selene.browsers import Browser
from selene.conditions import exact_text
from selene.tools import visit, s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def exception_message(ex):
    return str(ex.value).strip().splitlines()


def test_should_be_suppressed_exception_message_for_explicit_condition():
    with pytest.raises(TimeoutException) as ex:
        selene.config.browser_name = Browser.CHROME
        visit(start_page)
        s("#selene_link").should_have(exact_text("Selene sit"))
    assert exception_message(ex) == ['Message: ',
                                     '            failed while waiting 4 seconds',
                                     '            to assert exact_text',
                                     "            for element located by: Selene.find(('css selector', '#selene_link'))",
                                     '            \texpected: Selene sit',
                                     '            \t  actual: Selene site',
                                     "",
                                     "            reason: Condition Mismatch"]


def test_should_be_suppressed_exception_message_for_implicit_condition():
    with pytest.raises(TimeoutException) as ex:
        selene.config.browser_name = Browser.CHROME
        visit(start_page)
        s("#hidden_button").click()
    assert exception_message(ex) == ['Message: ',
                                     '            failed while waiting 4 seconds',
                                     '            to assert Visible',
                                     "            for element located by: Selene.find(('css selector', '#hidden_button'))",
                                     '            \texpected: ',
                                     '            \t  actual: ',
                                     "",
                                     "            reason: Condition Mismatch"]
