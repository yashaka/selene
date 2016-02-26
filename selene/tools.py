from selene import config
from selene.elements import SElement, SElementsCollection


def set_driver(driver):
    config.driver = driver


def get_driver():
    return config.driver


def visit(absolute_or_relative_url):
    """
    Loads a web page in the current browser session.
    :param absolute_or_relative_url:
        an absolute url to web page in case of config.app_host is not specified,
        otherwise - relative url correspondingly

    :Usage:
        visit('http://mydomain.com/subpage1')
        visit('http://mydomain.com/subpage2')
        # OR
        config.app_host = 'http://mydomain.com'
        visit('/subpage1')
        visit('/subpage2')
    """
    get_driver().get(config.app_host + absolute_or_relative_url)


def s(css_selector_or_locator):
    return SElement(css_selector_or_locator)


def ss(css_selector_or_locator, of=SElement):
    return SElementsCollection(css_selector_or_locator, of=of)

