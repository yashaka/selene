import pytest
from selenium.webdriver.common.by import By

from selene.support import by


def test_basic_locators():
    assert by.css('.item') == (By.CSS_SELECTOR, '.item')
    assert by.xpath('//div') == (By.XPATH, '//div')
    assert by.id('name') == (By.ID, 'name')
    assert by.class_name('active') == (By.CLASS_NAME, 'active')
    assert by.name('email') == (By.NAME, 'email')
    assert by.link_text('Docs') == (By.LINK_TEXT, 'Docs')
    assert by.partial_link_text('Doc') == (By.PARTIAL_LINK_TEXT, 'Doc')


def test_text_and_partial_text_build_xpath_with_quote_escape():
    locator = by.text('he said "hi"')
    partial = by.partial_text('he said "hi"')

    assert locator[0] == By.XPATH
    assert partial[0] == By.XPATH
    assert 'concat("", "he said ' in locator[1]
    assert 'normalize-space(.)' in locator[1]
    assert 'contains(normalize-space(.)' in partial[1]


def test_deprecated_navigation_helpers():
    with pytest.warns(DeprecationWarning):
        sibling = by.be_following_sibling('li')
    with pytest.warns(DeprecationWarning):
        parent = by.be_parent()
    with pytest.warns(DeprecationWarning):
        first = by.be_first_child('span')

    assert sibling == (By.XPATH, './following-sibling::li')
    assert parent == (By.XPATH, '..')
    assert first == (By.XPATH, './span[1]')


def test_escape_text_quotes_for_xpath_with_double_quotes():
    escaped_quote = """'"'"""

    assert by._escape_text_quotes_for_xpath('he said "hi"') == (
        f'concat("", "he said ", {escaped_quote}, "hi", {escaped_quote}, "")'
    )


def test_text_builds_exact_xpath_with_escaped_double_quotes():
    escaped_quote = """'"'"""

    assert by.text('he said "hi"') == (
        By.XPATH,
        './/*[text()[normalize-space(.) = '
        f'concat("", "he said ", {escaped_quote}, "hi", {escaped_quote}, "")]]',
    )


def test_partial_text_builds_contains_xpath_with_escaped_double_quotes():
    escaped_quote = """'"'"""

    assert by.partial_text('he said "hi"') == (
        By.XPATH,
        './/*[text()[contains(normalize-space(.), '
        f'concat("", "he said ", {escaped_quote}, "hi", {escaped_quote}, ""))]]',
    )


def test_deprecated_navigation_helpers_with_default_tag():
    with pytest.warns(DeprecationWarning):
        sibling = by.be_following_sibling()

    with pytest.warns(DeprecationWarning):
        first = by.be_first_child()

    assert sibling == (By.XPATH, './following-sibling::*')
    assert first == (By.XPATH, './*[1]')
