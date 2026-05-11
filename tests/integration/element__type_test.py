from selene import have
import time

from selene.core.exceptions import TimeoutException

from tests.integration.helpers.givenpage import GivenPage


def test_type_appends_text(session_browser):
    browser = session_browser.with_(timeout=1)
    browser.config.hold_driver_at_exit = True
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input id="text-field" value="text"></input>
        '''
    )

    browser.element('#text-field').type(' appended')

    browser.element('#text-field').should(have.value('text appended'))


def test_type_waits_for_no_overlay(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <div
          id="overlay"
          style="display: block;
                background-color: rgba(0, 0, 0, 0.336);
                position: fixed;
                height: 100%;
                width: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000">
        </div>
        <input id="text-field" value="before"></input>
        '''
    )
    time_before = time.time()
    page.opened_with_body_with_timeout(
        '''
        <input id="text-field" value="before"></input>
        ''',
        0.25,
    )
    # # TODO: for some reason the following code will fail sometimes on jenkins
    #         with error telling that element is yet overlapped
    #         by <div id="overlay" style="display: block;
    #         o_O ???
    #         why does this happens? does our impl have bug?
    # page.execute_script_with_timeout(
    #     '''
    #     document.getElementById('overlay').style.display='none'
    #     ''',
    #     0.25,
    # )

    browser.element('#text-field').type(' after')

    time_spent = time.time() - time_before
    assert time_spent >= 0.25
    browser.element('#text-field').should(have.value('before after'))


def test_type_failure_when_overlapped(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <div
          id="overlay"
          style="display: block;
                background-color: rgba(0, 0, 0, 0.336);
                position: fixed;
                height: 100%;
                width: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000">
        </div>
        <input id="text-field" value="before"></input>
        '''
    )
    time_before = time.time()

    try:
        browser.element('#text-field').type(' after')

    except TimeoutException as error:
        time_spent = time.time() - time_before
        assert time_spent >= 1
        browser.element('#text-field').should(have.value('before'))
        assert (
            'Element: <input id="text-field" value="before">'
            '\n\tis overlapped by: <div id="overlay"'
        ) in error.msg


def test_type_waits_for_visibility(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input
            id="text-field"
            value="before"
            style="display: none">
        </input>
        '''
    )
    time_before = time.time()
    page.execute_script_with_timeout(
        '''
        document.getElementById('text-field').style.display='block'
        ''',
        0.25,
    )

    browser.element('#text-field').type(' after')

    time_spent = time.time() - time_before
    assert time_spent >= 0.25
    browser.element('#text-field').should(have.value('before after'))


def test_type_failure_when_invisible(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <input
            id="text-field"
            value="before"
            style="display: none">
        </input>
        '''
    )
    time_before = time.time()

    try:
        browser.element('#text-field').type(' after')

    except TimeoutException as error:
        time_spent = time.time() - time_before
        assert time_spent >= 1
        browser.element('#text-field').should(have.value('before'))
        assert (
            'Reason: JavascriptException: javascript error: '
            'element '
            '<input id="text-field" value="before" style="display: none"> '
            'is not visible\n'
        ) in error.msg


def test_type_when_initially_absent(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_with_body_with_timeout(
        '''
        <input
            id="text-field"
            value="before"
        </input>
        ''',
        0.25,
    )
    time_before = time.time()

    browser.element('#text-field').type(' after')

    time_spent = time.time() - time_before
    assert time_spent >= 0.25
    browser.element('#text-field').should(have.value('before after'))


def test_type_failure_when_absent(session_browser):
    browser = session_browser.with_(timeout=1).with_(
        wait_for_no_overlap_found_by_js=True
    )
    page = GivenPage(browser.driver)
    page.opened_empty()
    time_before = time.time()

    try:
        browser.element('#text-field').type(' after')

    except TimeoutException as error:
        time_spent = time.time() - time_before
        assert time_spent >= 1
        assert "no such element: Unable to locate" in error.msg
