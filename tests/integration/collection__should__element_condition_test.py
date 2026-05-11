import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_collection_should_accept_composed_element_condition(session_browser):
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


def test_collection_should_report_per_element_mismatch_for_composed_element_condition(
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

        pytest.fail('should have failed on element condition mismatch')

    except TimeoutException as error:
        message = str(error)

        assert 'Not matched elements among all' in message
        assert ".cached[1]" in message
        assert "'list' object has no attribute 'get_attribute'" not in message
