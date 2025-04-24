from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_search_is_lazy_on_creation_for_collection_and_indexed(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    # WHEN
    non_existent_element = session_browser.all('.non-existing').element_by(
        have.exact_text('Kate')
    )

    # THEN
    # Laziness means it doesn't crash during creation, only when used
    assert str(non_existent_element)


def test_search_happens_on_first_action(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    # WHEN
    element = session_browser.all('.will-appear').element_by(have.exact_text('Kate'))
    page.load_body(
        '''
        <ul>Hello to:
            <li class="will-appear">Bob</li>
            <li class="will-appear">Kate</li>
        </ul>
        '''
    )

    # THEN
    assert element().is_displayed() is True


def test_search_is_updated_on_later_action(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    element = session_browser.all('.will-appear').element_by(have.css_class('special'))

    page.load_body(
        '''
        <ul>Hello to:
            <li class="will-appear">Bob</li>
            <li class="will-appear special">Kate</li>
        </ul>
        '''
    )

    # WHEN / THEN
    assert element().is_displayed() is True

    # WHEN (DOM changes)
    page.load_body(
        '''
        <ul>Hello to:
            <li class="will-appear">Bob</li>
            <li class="will-appear special" style="display:none">Kate</li>
        </ul>
        '''
    )

    # THEN
    assert element().is_displayed() is False
