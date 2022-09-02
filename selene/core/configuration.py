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

from __future__ import annotations

from typing import Callable, Optional, Union, Dict, Tuple, Any, List
from functools import reduce
import re

from selene.common import fp
from selene.common.fp import F
from selene.common.none_object import _NoneObject
from selene.core.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from selene.core.wait import Wait, E


def _strip_underscored_prefix(name: str, prefix='') -> str:
    underscored = f'_{prefix}'
    return name[len(underscored) :] if name.startswith(underscored) else name


def _strip_first_underscore(name: str):
    return _strip_underscored_prefix(name, prefix='')


class Config:
    # todo: add hooks:
    #            hook_wait_command: Callable[[Command], None]
    #            hook_...
    #       consider impementing some hooks as generators...
    #       hook generally should allow to do some processing before and after e.g. command
    #       think on better name depending on hook type (generator vs standard fn)
    def __init__(
        self,
        driver: Optional[Union[WebDriver, Callable[[], WebDriver]]] = None,
        timeout: int = 4,
        hook_wait_failure: Optional[
            Callable[[TimeoutException], Exception]
        ] = None,
        base_url: str = '',
        set_value_by_js: bool = False,
        type_by_js: bool = False,
        click_by_js: bool = False,
        wait_for_no_overlap_found_by_js: bool = False,
        window_width: Optional[int] = None,
        window_height: Optional[int] = None,
        log_outer_html_on_failure: bool = False,
        # TODO: better name? now technically it's not a decorator but decorator_builder...
        # or decorator_factory...
        # yet in python they call it just «decorator with args» or «decorator with params»
        # so technically I am correct naming it simply _wait_decorator
        # by type hint end users yet will see the real signature
        # and hence guess its «builder-like» nature
        # yet... should we for verbosity distinguish options
        # that a decorator factories from options that are simple decorators?
        # maybe better time to decide on this will be once we have more such options :p
        _wait_decorator: Callable[
            [Wait[E]], Callable[[F], F]
        ] = lambda _: fp.identity,
    ):

        self._driver = driver
        self._timeout = timeout
        self._hook_wait_failure = hook_wait_failure
        '''
        todo: why we name it as hook_* why not handle_* ?
              what would be proper style?
        '''
        self._base_url = base_url
        self._set_value_by_js = set_value_by_js
        '''
        todo: will it work on mobile? probably no! why then we have it here? o_O
        '''
        self._type_by_js = type_by_js
        self._click_by_js = click_by_js
        self._wait_for_no_overlap_found_by_js = wait_for_no_overlap_found_by_js
        self._window_width = window_width
        self._window_height = window_height
        self._log_outer_html_on_failure = log_outer_html_on_failure
        '''
        todo: should we even keep it as part of core.configuration?
              taking into account that it does not work for mobile
              while we want the core of Selene to be versatile as much as psbl.
              probably we should move it to support.shared.config only
        '''
        self.__wait_decorator = _wait_decorator

    def as_dict(self, skip_empty=True):
        everything = self.__dict__

        without_empty_and_magic = {
            key: value
            for key, value in everything.items()
            if not (skip_empty and value is None) and not key.endswith('__')
        }

        def accumulate_with_stripped_self_class(
            accumulator: Tuple[Dict, List[str]], item: Tuple[str, Any]
        ):
            accumulated_dict, accumulated_raw_names = accumulator
            key, value = item

            mangling = f'_{self.__class__.__name__}'
            is_mangled = key.startswith(mangling)

            new_key = key[len(mangling) :] if is_mangled else key
            raw_name_addition = [new_key] if is_mangled else []

            return (
                {**accumulated_dict, new_key: value},
                [*accumulated_raw_names, *raw_name_addition],
            )

        with_stripped_mangling_by_self, mangled_raw_names = reduce(
            accumulate_with_stripped_self_class,
            without_empty_and_magic.items(),
            ({}, []),
        )

        without_mangled_by_others = {
            key: value
            for key, value in with_stripped_mangling_by_self.items()
            if key in mangled_raw_names
            or not re.sub(r'^_[a-zA-Z]+(__)', repl=r'\1', string=key, count=1)
            in mangled_raw_names
        }

        with_stripped_first_underscore = {
            _strip_first_underscore(key): value
            for key, value in without_mangled_by_others.items()
        }

        return with_stripped_first_underscore

    def with_(self, config: Config = None, **config_as_kwargs) -> Config:
        return self.__class__(
            **{
                **self.as_dict(),
                **(config.as_dict() if config else {}),
                **config_as_kwargs,
            }
        )

    @property
    def driver(self) -> Union[WebDriver, _NoneObject]:
        return (
            self._driver
            if isinstance(self._driver, WebDriver)
            else (
                self._driver()
                if callable(self._driver)
                else _NoneObject(
                    'expected Callable[[], WebDriver] inside property config.driver'
                )
            )
        )

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def hook_wait_failure(self) -> Callable[[TimeoutException], Exception]:
        return self._hook_wait_failure

    # def hook_wait_success(self)
    # def hook_wait(self)

    def wait(self, entity):
        return Wait(
            entity,
            at_most=self.timeout,
            or_fail_with=self.hook_wait_failure,
            _decorator=self.__wait_decorator,
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def set_value_by_js(self) -> bool:
        return self._set_value_by_js

    @property
    def type_by_js(self) -> bool:
        return self._type_by_js

    @property
    def click_by_js(self) -> bool:
        return self._click_by_js

    @property
    def wait_for_no_overlap_found_by_js(self) -> bool:
        return self._wait_for_no_overlap_found_by_js

    @property
    def window_width(self) -> Optional[int]:
        return self._window_width

    @property
    def window_height(self) -> Optional[int]:
        return self._window_height

    @property
    def log_outer_html_on_failure(self) -> bool:
        return self._log_outer_html_on_failure

    @property
    def _wait_decorator(self) -> Callable[[Wait[E]], Callable[[F], F]]:
        return self.__wait_decorator
