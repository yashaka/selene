from selene import config
from selene.driver import browser
from selene.elements import RootSElement, SElement, SElementsCollection


def visit(relative_url):
    return browser().get(config.app_host + relative_url)


def s(css_locator, context=RootSElement()):
    """ convenient method to build SElement, i.e. the finder for element on the page by locator """
    return SElement(css_locator, context)


def ss(element_or_locator, context=RootSElement()):
    """ convenient method to build SElementsCollection, i.e. the finder for all elements on the page by locator """
    return SElementsCollection(element_or_locator, context)


