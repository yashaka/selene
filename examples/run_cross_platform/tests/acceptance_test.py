from examples.run_cross_platform.wikipedia_e2e_tests.utils.locators import by
from selene import browser, have, be


def test_wikipedia_searches():
    # GIVEN
    browser.open()

    # WHEN
    browser.element(by.name(drd='Search Wikipedia')).click()
    browser.element(by.id(web='searchInput', drd='search_src_text')).type('Appium')

    # THEN
    results = browser.all(by(web='.suggestion-link', drd='#page_list_item_title'))
    results.should(have.size_greater_than(0))
    results.first.should(have.text('Appium'))

    # WHEN
    results.first.click()

    # THEN
    browser.element(by.text('Appium')).should(be.visible)
