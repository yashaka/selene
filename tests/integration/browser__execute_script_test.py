from tests.integration.helpers.givenpage import GivenPage


def test_scroll_to_element_via_js(function_browser):
    # GIVEN
    function_browser.driver.set_window_size(300, 200)
    GivenPage(function_browser.driver).opened_with_body(
        '''
        <div id="paragraph" style="margin: 400px">
        </div>
        <a id="not-viewable-link" href="#header"></a>
        <h1 id="header">Heading 1</h1>
        '''
    )

    # WHEN
    link = function_browser.element("#not-viewable-link")
    function_browser.driver.execute_script("arguments[0].scrollIntoView();", link())
    link.click()

    # THEN
    assert "header" in function_browser.driver.current_url
