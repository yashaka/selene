import contextlib
import os

from selenium.webdriver.common.by import By

import selene.config


@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


def merge(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def extend(obj, cls, *init_args, **init_kwargs):
    obj.__class__ = type(obj.__class__.__name__, (obj.__class__, cls), {})
    cls.__init__(obj, *init_args, **init_kwargs)


def take_screenshot(webdriver, path=None, filename=None):
    if not path:
        path = selene.config.reports_folder
    if not filename:
        filename = "screen_{id}".format(id=next(selene.config.counter))

    screenshot_path = os.path.join(path,
                                   "{}.png".format(filename))

    folder = os.path.dirname(screenshot_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    webdriver.get_screenshot_as_file(screenshot_path)
    return screenshot_path


def css_or_by_to_by(css_selector_or_by):
    # todo: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
    if isinstance(css_selector_or_by, tuple):
        return css_selector_or_by
    if isinstance(css_selector_or_by, str):
        return (By.CSS_SELECTOR, css_selector_or_by)
    raise TypeError('css_selector_or_by should be str with CSS selector or Tuple[by:str, value:str]')


def env(key, default=None):
    try:
        return os.environ.get(key, default)
    except KeyError:
        return None
