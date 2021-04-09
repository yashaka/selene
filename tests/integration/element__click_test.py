from tests.integration.helpers.givenpage import GivenPage


def test_click_waits_for_covering_preload_element_to_disappear(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        ''' <style>
             canvas {
              background-color: rgba(0, 0, 0, 0.336);
              position: fixed;
              height: 100%;
              width: 100%;
              top: 0;
              left: 0;
              z-index: 1000;
             }
            </style>

            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>       

            <p><canvas></canvas></p>'''
    )
    page.load_body_with_timeout(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>       

        ''',
        250,
    )

    session_browser.element('a').click()

    assert "second" in session_browser.driver.current_url
