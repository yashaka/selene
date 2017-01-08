import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.common.none_object import NoneObject
from selene.conditions import exact_text
from selene.tools import s, get_driver, set_driver
from tests.integration.helpers.givenpage import GivenPage

GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    driver = webdriver.Firefox()
    set_driver(driver)
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)


def teardown_module(m):
    config.timeout = original_timeout
    get_driver().quit()


def exception_message(ex):
    return str(ex.value).strip().splitlines()


def test_selement_search_fails_with_message_when_explicitly_waits_for_condition():
    GIVEN_PAGE.opened_with_body('''
    <label id='element'>Hello world!</label>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#element').should_have(exact_text('Hello wor'))

    assert exception_message(ex) == \
           ['Message: ',
            '            failed while waiting 0.1 seconds',
            '            to assert exact_text(Hello wor)',
            "            for element located by: ('css selector', '#element'),",
            '            \texpected: Hello wor',
            '            \t  actual: Hello world!',
            '',
            '            reason: Condition Mismatch']


def test_selement_search_fails_with_message_when_implicitly_waits_for_condition():
    GIVEN_PAGE.opened_with_body('''
    <button id='hidden-button' style='display:none'>You can't click me, ha ha! :P</button>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#hidden-button').click()
    assert exception_message(ex) == \
           ['Message: ',
            '            failed while waiting 0.1 seconds',
            '            to assert Visible',
            "            for element located by: ('css selector', '#hidden-button'),",
            '',
            '            reason: Condition Mismatch']


def test_inner_selement_search_fails_with_message_when_implicitly_waits_for_condition_mismatch_on_inner_element():
    GIVEN_PAGE.opened_with_body('''
    <div id='container'>
        <button id='hidden-button' style='display:none'>You can't click me, ha ha! :P</button>
    </div>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#container').element('#hidden-button').click()
    assert exception_message(ex) == \
        ['Message: ',
         '            failed while waiting 0.1 seconds',
         '            to assert Visible',
         "            for element located by: ('css selector', '#container').find(('css selector', '#hidden-button')),",
         '',
         '            reason: Condition Mismatch']


def test_inner_selement_search_fails_with_message_when_implicitly_waits_for_condition_mismatch_on_parent_element():
    GIVEN_PAGE.opened_with_body('''
    <div id='hidden-container' style='display:none'>
        <button id='button'>You still can't click me, ha ha! :P</button>
    </div>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#hidden-container').element('#button').click()

    # todo: consider removing second entrance of "failed wile waiting..." from the error message
    assert exception_message(ex) == \
        ['Message: ',
         '            failed while waiting 0.1 seconds',
         '            to assert Visible',
         "            for element located by: ('css selector', '#hidden-container').find(('css selector', '#button')),",
         '',
         '            reason: Message: ',
         '            failed while waiting 0.1 seconds',
         '            to assert Visible',
         "            for element located by: ('css selector', '#hidden-container'),",
         '',
         '            reason: Condition Mismatch']


def test_selement_search_fails_with_message_when_explicitly_waits_for_not_condition():
    GIVEN_PAGE.opened_with_body('''
    <label id='element'>Hello world!</label>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#element').should_not_have(exact_text('Hello world!'))

    assert exception_message(ex) == \
           ['Message: ',
            '            failed while waiting 0.1 seconds',
            '            to assert not exact_text(Hello world!)',
            "            for element located by: ('css selector', '#element'),",
            '            \texpected: not(Hello world!)',
            '            \t  actual: Hello world!',
            '',
            '            reason: Condition Mismatch']