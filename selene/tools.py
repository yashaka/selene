from selenium.webdriver.common.by import By

from selene import config
from selene.driver import browser
from selene.elements import RootSElement, SElement, SElementsCollection


def visit(relative_url):
    return browser().get(config.app_host + relative_url)


def s(locator_or_element, by=By.CSS_SELECTOR, context=RootSElement()):
    """ convenient method to build SElement, i.e. the finder for element on the page by locator """
    return SElement(locator_or_element, by, context)


def ss(locator_or_element, by=By.CSS_SELECTOR, context=RootSElement()):
    """ convenient method to build SElementsCollection, i.e. the finder for all elements on the page by locator """
    return SElementsCollection(locator_or_element, by, context)
