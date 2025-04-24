from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_counts_elements_with_invisible_items(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    # Define elements by their shared class but defer actual search
    elements = session_browser.all('li').by(have.css_class('will-appear'))

    page.load_body(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>
        '''
    )

    # WHEN
    count = len(elements)

    # THEN
    assert count == 2
