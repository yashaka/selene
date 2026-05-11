import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_collection_should_keeps_collection_condition_name(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body('''
        <ul>
            <li>One</li>
            <li>Two</li>
            <li>Three</li>
        </ul>
        ''')

    condition = have.size(2)

    try:
        browser.all('li').should(condition)

        pytest.fail('should have failed on collection size mismatch')

    except TimeoutException as error:
        message = str(error)

        assert f"browser.all(('css selector', 'li')).{condition}" in message
        assert 'actual size: 3' in message
        assert '<function Collection.should' not in message
        assert '<function' not in message
