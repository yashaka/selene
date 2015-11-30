from selene import config
from selene.elements import SElement, SElementsCollection


def set_driver(driver):
    config.driver = driver


def get_driver():
    return config.driver


def visit(relative_url):
    get_driver().get(config.app_host + relative_url)


def s(css_selector_or_locator):
    return SElement(css_selector_or_locator)


def ss(css_selector_or_locator):
    return SElementsCollection(css_selector_or_locator)

