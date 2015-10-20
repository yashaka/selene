from selene4 import config
from selene4.elements import SElement, SElementsCollection


def visit(url):
    config.driver.get(url)


def s(css_selector):
    return SElement(css_selector)


def ss(css_selector):
    return SElementsCollection(css_selector)

