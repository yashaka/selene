from selene import have, command
import time

from selene.core.exceptions import TimeoutException

from tests.integration.helpers.givenpage import GivenPage


def test_select_all_allows_to_overwrite_text_via_type(session_browser):
    browser = session_browser.with_(timeout=1)
    browser.config.hold_driver_at_exit = True
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )

    browser.element('#text-field').perform(command.select_all).type('new text')

    browser.element('#text-field').should(have.value('new text'))
