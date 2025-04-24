from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_collection_search_is_lazy_on_creation(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    # WHEN
    non_existent_collection = session_browser.all('.not-existing').by(
        have.css_class('special')
    )

    # THEN
    # Lazy search means it doesn’t raise an error on creation
    assert str(non_existent_collection)


def test_collection_search_is_triggered_on_first_action(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    elements = session_browser.all('li').by(have.css_class('will-appear'))

    page.load_body(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear'>Kate</li>
        </ul>
        '''
    )

    # WHEN
    count = len(elements)

    # THEN
    assert count == 2


def test_collection_search_updates_after_dom_changes(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    elements = session_browser.all('li').by(have.css_class('will-appear'))

    page.load_body(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear'>Kate</li>
        </ul>
        '''
    )
    original_count = len(elements)

    # WHEN
    page.load_body(
        '''
        <ul>Hello to:
            <li>Anonymous</li>
            <li class='will-appear'>Bob</li>
            <li class='will-appear'>Kate</li>
            <li class='will-appear'>Joe</li>
        </ul>
        '''
    )
    updated_count = len(elements)

    # THEN
    assert updated_count == 3
    assert updated_count != original_count
