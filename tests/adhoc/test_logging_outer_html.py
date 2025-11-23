import pytest

from selene import browser, have, be
from tests import resources


def test_logging_outer_html__enabled__on_one_element():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = True
    browser.open(resources.TODOMVC_URL)

    message = None
    try:
        browser.element('#new-todo').should(have.attribute('wrong_attr'))
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelement:' in message


def test_logging_outer_html__disabled__on_one_element():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = False
    browser.open('http://todomvc.com/examples/emberjs/')

    message = None
    try:
        browser.element('#new-todo').should(have.attribute('wrong_attr'))
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelement:' not in message


def test_logging_outer_html__enabled__on_collection():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = True
    browser.open(resources.TODOMVC_URL)

    # WHEN
    footer_paragraphs = browser.all('footer p')
    wrong_paragraph = footer_paragraphs.element_by(have.attribute('wrong_attr'))

    # THEN
    assert browser.config.log_outer_html_on_failure is True
    assert footer_paragraphs.config.log_outer_html_on_failure is True
    assert wrong_paragraph.config.log_outer_html_on_failure is True

    # WHEN
    message = None
    try:
        wrong_paragraph.should(be.visible)
        pytest.fail('should have failed')
    except Exception as e:
        # THEN
        message = str(e)

    # AND
    assert message is not None
    # TODO: FIX – no 'Actual webelements collection' in message
    assert 'Actual webelements collection:' in message


def test_logging_outer_html__disabled__on_collection():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = False
    browser.open('http://todomvc.com/examples/emberjs/')

    message = None
    try:
        browser.all('footer p').element_by(have.attribute('wrong_attr')).should(
            be.visible
        )
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelements collection:' not in message
