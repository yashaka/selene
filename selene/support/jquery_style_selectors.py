from selene import browser


def s(css_selector_or_by):
    return browser.element(css_selector_or_by)


def ss(css_selector_or_by):
    return browser.elements(css_selector_or_by)