from selene.support._pom import element, all_


def test__pom__element_is_unique_for_each_object():
    class Page:
        selector = '.element'
        element = element(selector)
        elements = all_(selector)

    page1 = Page()
    page2 = Page()

    assert page1.selector is page2.selector
    # but
    assert page1.element is not page2.element
    assert page1.elements is not page2.elements
    # while
    assert page1.element is page1.element
    assert page1.elements is page1.elements
    assert page2.element is page2.element
    assert page2.elements is page2.elements
