from selene import query
from tests.integration.helpers.givenpage import GivenPage


def test_returns_inner_htmls_of_elements(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <ul>Hello:
           <li>Alex!</li>
           <li>  Yakov! \n </li>
        </ul>
        '''
    )

    # WHEN
    inner_htmls = session_browser.all('li').get(query.inner_htmls)

    # THEN
    assert inner_htmls == [
        'Alex!',
        '  Yakov!   ',
    ]
