from selene.support.shared import browser
from selene import have, be


def test_one_element_when_enabled():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = True
    browser.open('http://todomvc.com/examples/emberjs/')

    message = None
    try:
        browser.element('#new-todo').should(have.attribute('wrong_attr'))
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelement:' in message


def test_one_element_when_disabled():
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


def test_collection_when_enabled():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = True
    browser.open('http://todomvc.com/examples/emberjs/')

    message = None
    try:
        browser.all('footer p').element_by(
            have.attribute('wrong_attr')
        ).should(be.visible)
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelements collection:' in message


def test_collection_when_disabled():
    browser.config.timeout = 0.5
    browser.config.log_outer_html_on_failure = False
    browser.open('http://todomvc.com/examples/emberjs/')

    message = None
    try:
        browser.all('footer p').element_by(
            have.attribute('wrong_attr')
        ).should(be.visible)
    except Exception as e:
        message = str(e)

    assert message is not None
    assert 'Actual webelements collection:' not in message
