import contextlib
import os

from selenium.webdriver.common.by import By


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

def css_or_by_to_by(css_selector_or_by):
    # todo: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
    if isinstance(css_selector_or_by, tuple):
        return css_selector_or_by
    if isinstance(css_selector_or_by, str):
        return (By.CSS_SELECTOR, css_selector_or_by)
    raise TypeError('css_selector_or_by should be str with CSS selector or Tuple[by:str, value:str]')
