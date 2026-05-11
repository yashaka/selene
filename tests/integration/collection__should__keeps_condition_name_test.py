import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_collection_should_keeps_entity_aware_condition_name(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li>One</li>
            <li>Two</li>
            <li>Three</li>
        </ul>
        ''')

    try:
        browser.all('li').should(have.size(2))

        pytest.fail('should have failed on collection size mismatch')

    except TimeoutException as error:
        message = str(error)

        assert "browser.all(('css selector', 'li')).have size 2" in message
        assert "browser.all(('css selector', 'li')).has size 2" not in message
