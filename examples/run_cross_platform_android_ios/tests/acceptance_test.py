from selene import have, be
from selene.support._mobile import device


def test_wikipedia_searches():
    # GIVEN
    device.element('fragment_onboarding_skip_button').tap()

    # WHEN
    device.element(drd='Search Wikipedia').tap()
    device.element('search_src_text').type('Appium')

    # THEN
    results = device.all('page_list_item_title')
    results.should(have.size_greater_than(0))
    results.first.should(have.text('Appium'))

    # WHEN
    results.first.tap()

    # THEN
    device.element('text=Appium').should(be.visible)
