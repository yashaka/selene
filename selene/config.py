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
from typing import Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

# todo: consider making these dataclasses be Mapping-like, so can be used in the 'dict' context
from selene.common import fp
from selene.common.helpers import as_dict


@dataclass(frozen=True)
class WaitHooks:
    failure: Callable[[TimeoutException], Exception]


@dataclass(frozen=True)
class Hooks:
    wait: WaitHooks = WaitHooks(failure=fp.identity)


@dataclass(frozen=True)
class Config:  # todo: consider making a base Config class unfrozen, and then use frozen version in browser
    driver: WebDriver = None
    timeout: int = 4
    base_url: str = ''
    set_value_by_js: bool = False
    type_by_js: bool = False
    window_width: int = None
    window_height: int = None
    hooks: Hooks = Hooks()

    def with_(self, config: Config = None, **config_as_kwargs) -> Config:
        return self.__class__(**{**as_dict(self), **as_dict(config), **config_as_kwargs})
