from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_does_not_wait_for_updated_elements(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    # Define a lazy-evaluated filtered collection
    elements = session_browser.all('li').by(have.css_class('will-appear'))

    # Load initial body with two matching elements (one hidden)
    page.load_body(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>
        '''
    )
    original_count = len(elements)

    # WHEN
    # Load new element after a delay, but no new evaluation is triggered
    page.load_body_with_timeout(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
            <li class='will-appear'>Joe</li>
        </ul>
        ''',
        timeout=0.5,
    )

    updated_count = len(elements)

    # THEN
    assert updated_count == original_count == 2
