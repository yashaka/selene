from selene import have, command

from tests.integration.helpers.givenpage import GivenPage


def test_select_all_called_on_element_makes_type_to_reset_text(session_browser):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="text"></input>
        '''
    )

    browser.element('#text-field').select_all().type('reset')

    browser.element('#text-field').should(have.value('reset'))


# TODO: should we move it to browser__perform__select_all_test.py?
def test_select_all_called_on_browser_makes_type_to_reset_text_on_focused_element(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="text"></input>
        '''
    )
    browser.element('#text-field').click()  # <- GIVEN

    browser.perform(command.select_all)
    browser.element('#text-field').type('reset')

    browser.element('#text-field').should(have.value('reset'))


def test_select_all_called_on_browser_makes_type_to_append_text_on_not_focused_element(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="text"></input>
        '''
    )
    # browser.element('#text-field').click()  # <- GIVEN

    browser.perform(command.select_all)
    browser.element('#text-field').type(' to append')

    browser.element('#text-field').should(have.value('text to append'))
