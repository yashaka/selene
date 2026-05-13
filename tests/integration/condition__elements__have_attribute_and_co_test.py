import pytest

from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_have_no_attribute_value_containing_does_not_raise_type_error(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <input id="firstname" class="name" value="John">
    ''')

    browser.element('.name').should(have.no.attribute('id').value_containing('last'))

    with pytest.raises(AssertionError):
        browser.element('.name').should(
            have.no.attribute('id').value_containing('first')
        )


def test_have_no_attribute_descriptor_methods_work(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <input class="name" id="firstname" value="John">
        <input class="name" id="lastname" value="Doe">
    ''')

    name = browser.element('.name')
    names = browser.all('.name')

    name.should(have.no.attribute('id').value('lastname'))
    name.should(have.no.attribute('id').value_containing('last'))

    names.should(have.no.attribute('id').values('foo', 'bar'))
    names.should(have.no.attribute('id').values_containing('foo', 'bar'))

    with pytest.raises(AssertionError):
        name.should(have.no.attribute('id').value('firstname'))

    with pytest.raises(AssertionError):
        name.should(have.no.attribute('id').value_containing('first'))

    with pytest.raises(AssertionError):
        names.should(have.no.attribute('id').values('firstname', 'lastname'))

    with pytest.raises(AssertionError):
        names.should(have.no.attribute('id').values_containing('first', 'last'))


def test_have_attribute_href_value_uses_dom_attribute_not_absolute_url(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <a class="nav" href="#second">go to Heading 2</a>
    ''')

    browser.element('.nav').should(have.attribute('href').value('#second'))


def test_have_attribute_href_values_uses_dom_attribute_not_absolute_urls(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <a class="nav" href="#first">go to Heading 1</a>
        <a class="nav" href="#second">go to Heading 2</a>
    ''')

    browser.all('.nav').should(have.attribute('href').values('#first', '#second'))


def test_have_attribute_src_value_uses_dom_attribute_not_absolute_url(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <img class="logo" src="images/logo.png" />
    ''')

    browser.element('.logo').should(have.attribute('src').value('images/logo.png'))


def test_have_attribute_id_value_keeps_default_get_attribute_behavior(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <input class="name" id="firstname" value="John">
    ''')

    browser.element('.name').should(have.attribute('id').value('firstname'))
