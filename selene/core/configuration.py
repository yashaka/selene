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

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

# todo: consider making these dataclasses be Mapping-like, so can be used in the 'dict' context
from selene.common import fp


# todo: should we unfreeze them too? as we did with Config?
@dataclass(frozen=True)
class WaitHooks:
    failure: Callable[[TimeoutException], Exception]


@dataclass(frozen=True)
class Hooks:
    wait: WaitHooks = WaitHooks(failure=fp.identity)


def _strip_first_underscore(name: str) -> str:
    return name[1:] if name.startswith('_') else name


class Config:
    def __init__(self,
                 driver: Optional[WebDriver] = None,
                 timeout: int = 4,
                 base_url: str = '',
                 set_value_by_js: bool = False,
                 type_by_js: bool = False,
                 window_width: Optional[int] = None,
                 window_height: Optional[int] = None,
                 hooks: Hooks = Hooks()):
        self._driver = driver
        self._timeout = timeout
        self._base_url = base_url
        self._set_value_by_js = set_value_by_js
        self._type_by_js = type_by_js
        self._window_width = window_width
        self._window_height = window_height
        self._hooks = hooks

    def as_dict(self, skip_empty=True):
        return {_strip_first_underscore(k): v
                for k, v in self.__dict__.items()
                if not (skip_empty and v is None) and not k.startswith('__')
                }

    def with_(self, config: Config = None, **config_as_kwargs) -> Config:
        return self.__class__(**{**self.as_dict(),
                                 **(config.as_dict() if config else {}),
                                 **config_as_kwargs})

    @property
    def driver(self) -> Optional[WebDriver]:
        return self._driver

    @property
    def timeout(self) -> int:
        return self._timeout

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
    def window_width(self) -> Optional[int]:
        return self._window_width

    @property
    def window_height(self) -> Optional[int]:
        return self._window_height

    @property
    def hooks(self) -> Hooks:
        return self._hooks
