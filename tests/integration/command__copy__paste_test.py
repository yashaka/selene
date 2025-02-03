"""
Reflects main scenarios from docs/faq/clipboard-copy-and-paste-howto.md
(those that uses either command.copy or command.paste explicitly or implicitly)
"""

from selene import have, command
import pyperclip
from tests.integration.helpers.givenpage import GivenPage


def test_copy_currently_selected_text_on_the_page_into_clipboard_via_shortcut(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    browser.element('#text-field').select_all()

    browser.perform(command.copy)

    assert pyperclip.paste() == 'old text'


def test_paste_into_currently_focused_element_a_text_from_clipboard_via_shortcut(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    pyperclip.copy(' new text')
    browser.element('#text-field').click()

    browser.perform(command.paste)

    browser.element('#text-field').should(have.value('old text new text'))


def test_paste_into_currently_selected_all_input_a_text_from_clipboard_via_shortcut(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    pyperclip.copy('new text')
    browser.element('#text-field').select_all()

    browser.perform(command.paste)

    browser.element('#text-field').should(have.value('new text'))


def test_put_text_in_clipboard_then_paste_it_into_currently_focused_element_via_shortcut(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    browser.element('#text-field').click()

    browser.perform(command.paste(' new text'))

    browser.element('#text-field').should(have.value('old text new text'))


def test_select_value_of_an_input_element_then_copy_it_into_clipboard_via_shortcut(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="new text to copy"></input>
        '''
    )
    pyperclip.copy('OLD TEXT')

    browser.element('#text-field').select_all().copy()

    assert pyperclip.paste() == 'new text to copy'


def test_paste_via_shortcut_text_into_text_input_at_current_cursor_position(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    pyperclip.copy(' new text')

    browser.element('#text-field').paste()

    browser.element('#text-field').should(have.value('old text new text'))


def test_paste_via_shortcut_text_into_text_input_substituting_current_text(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )
    pyperclip.copy('new text')

    browser.element('#text-field').select_all().paste()

    browser.element('#text-field').should(have.value('new text'))


def test_copy_text_then_paste_it_via_shortcut_at_current_cursor_position(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )

    browser.element('#text-field').paste(' new text')

    browser.element('#text-field').should(have.value('old text new text'))


def test_copy_text_then_paste_it_via_shortcut_substituting_current_text(
    session_browser,
):
    browser = session_browser.with_(timeout=1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <input id="text-field" value="old text"></input>
        '''
    )

    browser.element('#text-field').select_all().paste('new text')

    browser.element('#text-field').should(have.value('new text'))
