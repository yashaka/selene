from tests.integration.helpers.givenpage import GivenPage


def test_counts_invisible_tasks(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    page.load_body(
        '''
        <ul>Hello to:
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>
        '''
    )

    # WHEN
    elements = session_browser.all('.will-appear')
    count = len(elements)

    # THEN
    assert count == 2
