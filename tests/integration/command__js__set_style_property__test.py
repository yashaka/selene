import time

from selene import command
from tests.integration.helpers.givenpage import GivenPage


def test_set_style_property_can_hide_element(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <div
            id="overlay"
            style='
                display:block;
                position: fixed;
                display: block;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0,0,0,0.1);
                z-index: 2;
                cursor: pointer;
            '
        >
        </div>
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    )

    browser.element('#overlay').perform(
        command.js.set_style_property('display', 'none')
    )
    browser.element('a').click()

    assert "second" in browser.driver.current_url


def test_set_style_property_can_hide_all_elements(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <div
            role="overlay"
            style='
                display:block;
                position: fixed;
                display: block;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0,0,0,0.1);
                z-index: 2;
                cursor: pointer;
            '
        >
        </div>
        <div
            role="overlay"
            style='
                display:block;
                position: fixed;
                display: block;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0,0,0,0.1);
                z-index: 2;
                cursor: pointer;
            '
        >
        </div>
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    )

    browser.all('[role=overlay]').perform(
        command.js.set_style_property('display', 'none')
    )
    browser.element('a').click()

    assert "second" in browser.driver.current_url
