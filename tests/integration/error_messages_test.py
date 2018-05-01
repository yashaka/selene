import pytest
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene import browser
from selene import config
from selene.common.none_object import NoneObject
from selene.support.conditions import have
from selene.support.jquery_style_selectors import s, ss
from tests.integration.helpers.givenpage import GivenPage

GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    driver = webdriver.Firefox()
    browser.set_driver(driver)
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)


def teardown_module(m):
    config.timeout = original_timeout
    browser.driver().quit()


def exception_message(ex):
    return [line.strip() if not re.match('\s*screenshot: .*?/\.selene/screenshots/\d+?/screen_\d+\.png\s*',line)
            else 'screenshot: //.selene/screenshots/*/screen_*.png'
            for line in str(ex.value.msg).strip().splitlines()]


def test_selement_search_fails_with_message_when_explicitly_waits_for_condition():
    GIVEN_PAGE.opened_with_body('''
    <label id='element'>Hello world!</label>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#element').should(have.exact_text('Hello wor'))

    assert exception_message(ex) == \
           ['failed while waiting 0.1 seconds',
            'to assert ExactText',
            "for first_by('css selector', '#element')",
            '',
            'reason: ConditionMismatchException: condition did not match',
            "expected: Hello wor",
            "actual: Hello world!",
            'screenshot: //.selene/screenshots/*/screen_*.png']


def test_selement_search_fails_with_message_when_implicitly_waits_for_condition():
    GIVEN_PAGE.opened_with_body('''
    <button id='hidden-button' style='display:none'>You can't click me, ha ha! :P</button>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#hidden-button').click()
    assert exception_message(ex) == \
           ['failed while waiting 0.1 seconds',
            'to assert Visible',
            "for first_by('css selector', '#hidden-button')",
            '',
            'reason: ConditionMismatchException: condition did not match',
            'screenshot: //.selene/screenshots/*/screen_*.png']


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
        ['failed while waiting 0.1 seconds',
         'to assert Visible',
         "for first_by('css selector', '#container').find_by('css selector', '#hidden-button')",
         '',
         'reason: ConditionMismatchException: condition did not match',
         'screenshot: //.selene/screenshots/*/screen_*.png']


def test_inner_selement_search_fails_with_message_when_implicitly_waits_for_condition_mismatched_on_parent_element():
    GIVEN_PAGE.opened_with_body('''
    <div id='hidden-container' style='display:none'>
        <button id='button'>You still can't click me, ha ha! :P</button>
    </div>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#hidden-container').element('#button').click()

    assert exception_message(ex) == \
        ['failed while waiting 0.1 seconds',
         'to assert Visible',
         "for first_by('css selector', '#hidden-container').find_by('css selector', '#button')",
         '',
         'reason: ConditionMismatchException: condition did not match',
         'screenshot: //.selene/screenshots/*/screen_*.png']


def test_inner_selement_search_fails_with_message_when_implicitly_waits_for_condition_failed_on_parent_element():
    GIVEN_PAGE.opened_with_body('''
    <div>
        <button id='button'>Try to click me</button>
    </div>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        s('#not-existing').element('#button').click()

    assert exception_message(ex) == \
        ['failed while waiting 0.1 seconds',
         'to assert Visible',
         "for first_by('css selector', '#not-existing').find_by('css selector', '#button')",
         '',
         'reason: TimeoutException:',
         'failed while waiting 0.1 seconds',
         'to assert InDom',
         "for first_by('css selector', '#not-existing')",
         '',
         'reason: NoSuchElementException: Unable to locate element: {"method":"css selector","selector":"#not-existing"}',
         'screenshot: //.selene/screenshots/*/screen_*.png']


def test_indexed_selement_search_fails_with_message_when_implicitly_waits_for_condition_failed_on_collection():
    GIVEN_PAGE.opened_with_body('''
    <div>
        <button id='button'>Try to click me</button>
    </div>
    ''')
    config.timeout = 0.1

    with pytest.raises(TimeoutException) as ex:
        ss('button')[1].click()

    assert exception_message(ex) == \
        ['failed while waiting 0.1 seconds',
         'to assert Visible',
         "for all_by('css selector', 'button')[1]",
         '',
         'reason: TimeoutException:',
         'failed while waiting 0.1 seconds',
         'to assert SizeAtLeast',
         "for all_by('css selector', 'button')",
         '',
         'reason: ConditionMismatchException: condition did not match',
         'expected: >= 2',
         'actual: 1',
         'screenshot: //.selene/screenshots/*/screen_*.png']

# todo: uncomment when refactored conditions implementation
# def test_selement_search_fails_with_message_when_explicitly_waits_for_not_condition():
#     GIVEN_PAGE.opened_with_body('''
#     <label id='element'>Hello world!</label>
#     ''')
#     config.timeout = 0.1
#
#     s('#element').should_not(have.exact_text('Hello world!'))
#     with pytest.raises(TimeoutException) as ex:
#         s('#element').should_not(have.exact_text('Hello world!'))
#
#     assert exception_message(ex) == \
#            ['failed while waiting 0.1 seconds',
#             'to assert not ExactText',
#             "for first_by('css selector', '#element')",
#             '',
#             'reason: ConditionMismatchException: condition did not match',
#             'expected: not(Hello world!)',
#             'actual: Hello world!',
#             'screenshot: //.selene/screenshots/*/screen_*.png']
