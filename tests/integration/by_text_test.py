from selene import by
from tests.integration.helpers.givenpage import GivenPage


def test_navigates_to_nested_third_heading(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <div id="container">
            <div>
                <div>
                    <label>First</label>
                </div>
                <div>
                    <a href="#first">go to Heading 1</a>
                </div>
            </div>
            <div>
                <div>
                    <label>Second</label>
                    <div>
                        <a href="#second">go to Heading 2</a>
                        <a href="#third">go to "Heading 'Third'"</a>
                    </div>
                </div>
                <div>
                </div>
            </div>
        </div>
        <h1 id="first">Heading 1</h1>
        <h2 id="second">Heading 2</h2>
        <h2 id="third">Heading 3</h2>
        '''
    )

    # WHEN
    session_browser.element('#container')\
        .element(by.text('Second'))\
        .element('./following-sibling::*')\
        .element(by.partial_text("Heading 'Third'"))\
        .click()

    # THEN
    assert "third" in session_browser.driver.current_url
