from tests.integration.helpers.givenpage import GivenPage


def test_click_waits_for_no_overlay(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        <div>
          id=overlay,
          style="display: block;
                background-color: rgba(0, 0, 0, 0.336),
                position: fixed,
                height: 100%,
                width: 100%,
                top: 0,
                left: 0,
                z-index: 1000"
        </div>
        '''
    )
    page.execute_script_with_timeout(
        '''
        document.getElementById('overlay').style.display=none
        ''',
        250,
    )

    browser.element('a').click()

    assert "second" in browser.driver.current_url
