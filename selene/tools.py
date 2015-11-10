from selenium.webdriver.common.by import By

from selene import settings
from selene.driver import browser
from selene.elements import RootSElement, SElement, SElementsCollection


def visit(url='', relative=True):
    """
    This method allows to open any URL. If you specify relative URL then "config.app_host + url" will be loaded.

    :param url: relative or absolute URL
    :param relative: shows is URL relative or not (default = True)
    :return: instance of browser
    """
    if relative:
        to_open = settings.app_host
        if not to_open.endswith('/'):
            to_open += '/'
        if url.startswith('/'):
            to_open += url.replace('/', '', 1)
        else:
            to_open += url
        return browser().get(to_open)
    else:
        return browser().get(url)


def s(locator_or_element, by=By.CSS_SELECTOR, context=RootSElement(), loading_time=settings.time_of_element_appearence):
    """ convenient method to build SElement, i.e. the finder for element on the page by locator """
    return SElement(locator_or_element, by, context, loading_time=loading_time)


def ss(locator_or_element, by=By.CSS_SELECTOR, context=RootSElement(),
       loading_time=settings.time_of_element_appearence):
    """ convenient method to build SElementsCollection, i.e. the finder for all elements on the page by locator """
    return SElementsCollection(locator_or_element, by, context, loading_time=loading_time)


def execute_script(script, element=None):
    if element:
        from selenium.webdriver.remote.webelement import WebElement
        return browser().execute_script(script, WebElement(element.parent, element.id))
    else:
        return browser().execute_script(script)


def remove_read_only(element):
    return execute_script("arguments[0].removeAttribute('readonly','readonly')", element)
