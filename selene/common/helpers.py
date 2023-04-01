# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
from typing import Union, Tuple, Iterable, Any

from selenium.webdriver.common.by import By


def as_dict(o, skip_empty=True):
    return (
        {
            k: v
            for k, v in o.__dict__.items()
            if not (skip_empty and v is None) and not k.startswith('_')
        }
        if o
        else {}
    )


def to_by(selector_or_by: Union[str, Tuple[str, str]]) -> Tuple[str, str]:
    # TODO: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
    if isinstance(selector_or_by, tuple):
        return selector_or_by
    if isinstance(selector_or_by, str):
        return (
            (By.XPATH, selector_or_by)
            if (
                selector_or_by.startswith('/')
                or selector_or_by.startswith('./')
                or selector_or_by.startswith('..')
                or selector_or_by.startswith('(')
            )
            else (By.CSS_SELECTOR, selector_or_by)
        )
    raise TypeError(
        'selector_or_by should be str with CSS selector or XPATH selector or Tuple[by:str, value:str]'
    )


def flatten(collection: Iterable[Union[Iterable[Any], Any]]) -> Iterable[Any]:
    # TODO: consider adding skip_none=False option
    return tuple(  # TODO: refactor to return tuple
        item_or_inner
        for item in collection
        for item_or_inner in (
            item
            if (isinstance(item, Iterable) and not isinstance(item, str))
            else [item]
        )
    )


def dissoc(associated: dict, *keys: str) -> dict:
    return {k: v for k, v in associated.items() if k not in keys}


def on_error_return_false(no_args_predicate):
    try:
        return no_args_predicate()
    except Exception:
        return False


def is_absolute_url(relative_or_absolute_url: str) -> bool:
    url = relative_or_absolute_url.lower()
    return (
        url.startswith('http:')
        or url.startswith('https:')
        or url.startswith('file:')
        or url.startswith('about:')
        or url.startswith('data:')
    )
