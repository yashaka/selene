from selene import config
from selene.elements import SElement, SElementsCollection


def set_driver(driver):
    config.driver = driver


def get_driver():
    return config.driver


def visit(url='', relative=True):
    """
    This method allows to open any URL. If you specify relative URL then "config.app_host + url" will be loaded.

    :param url: relative or absolute URL
    :param relative: shows is URL relative or not (default = True)
    :return: instance of driver
    """
    if relative:
        to_open = config.app_host
        if not to_open.endswith('/') and url:
            to_open += '/'
        if url.startswith('/'):
            to_open += url.replace('/', '', 1)
        else:
            to_open += url
        return get_driver().get(to_open)
    else:
        return get_driver().get(url)


def s(css_selector_or_locator):
    return SElement(css_selector_or_locator)


def ss(css_selector_or_locator):
    return SElementsCollection(css_selector_or_locator)
