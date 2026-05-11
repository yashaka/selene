import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_collection_should_accept_or_of_element_text_conditions(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li class="cell">Bob Flemming</li>
            <li class="cell">Flemming Bob</li>
            <li class="cell">FLEMMING BOB</li>
        </ul>
        ''')

    cells = browser.all('.cell')

    cells.should(
        have.text('Bob Flemming')
        .or_(have.text('Flemming Bob'))
        .or_(have.text('FLEMMING BOB'))
    )


def test_collection_should_accept_and_of_element_attribute_conditions(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li class="dropdown-list-item dropdown-list-item-disabled"
                aria-disabled="true">First</li>
            <li class="dropdown-list-item dropdown-list-item-disabled"
                aria-disabled="true">Second</li>
            <li class="dropdown-list-item dropdown-list-item-disabled"
                aria-disabled="true">Third</li>
        </ul>
        ''')

    browser.all('.dropdown-list-item').should(
        have.css_class('dropdown-list-item-disabled').and_(
            have.attribute('aria-disabled').value('true')
        )
    )


def test_collection_should_report_composed_element_condition_mismatch_per_item(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li class="dropdown-list-item dropdown-list-item-disabled"
                aria-disabled="true">First</li>
            <li class="dropdown-list-item"
                aria-disabled="false">Second</li>
            <li class="dropdown-list-item dropdown-list-item-disabled"
                aria-disabled="true">Third</li>
        </ul>
        ''')

    try:
        browser.all('.dropdown-list-item').should(
            have.css_class('dropdown-list-item-disabled').and_(
                have.attribute('aria-disabled').value('true')
            )
        )

        pytest.fail('should have failed on second item')

    except TimeoutException as error:
        message = str(error)

        assert 'Not matched elements among all' in message
        assert ".cached[1]" in message
        assert "'list' object has no attribute" not in message


def test_collection_should_keep_collection_conditions_applied_to_collection(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li class="cell">Bob Flemming</li>
            <li class="cell">Flemming Bob</li>
        </ul>
        ''')

    browser.all('.cell').should(have.texts('Bob Flemming', 'Flemming Bob'))
