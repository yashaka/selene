# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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


def css_or_by_to_by(selector_or_by):
    # todo: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
    if isinstance(selector_or_by, tuple):
        return selector_or_by
    if isinstance(selector_or_by, str):
        return (By.XPATH, selector_or_by) if (selector_or_by.startswith('/') or selector_or_by.startswith('./')) \
            else (By.CSS_SELECTOR, selector_or_by)
    raise TypeError('selector_or_by should be str with CSS selector or XPATH selector or Tuple[by:str, value:str]')


def env(key, default=None):
    try:
        return os.environ.get(key, default)
    except KeyError:
        return None
