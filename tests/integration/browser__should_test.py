import os
import pytest

from selene import browser, have
from tests.integration.helpers.givenpage import GivenPage


def test_waits_for_url_containing(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <a id="delayed-link" href="#second">Go to second</a>
        <script>
            setTimeout(function() {
                document.getElementById("delayed-link").click();
            }, 500);
        </script>
        '''
    )

    # WHEN / THEN
    browser.should(have.url_containing('#second'))
    assert 'second' in browser.driver.current_url
