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

import abc
import itertools
import typing
from abc import ABC, abstractmethod
from types import MappingProxyType

from typing_extensions import Literal, Dict, cast

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.common.service import Service

from selene.common.fp import pipe as pipe, F
from selene.common.helpers import (
    flatten as flatten,
    is_absolute_url as is_absolute_url,
)
from selene.core.condition import Condition as Condition
from selene.core.configuration import Config as Config
from selene.core.exceptions import TimeoutException as TimeoutException
from selene.core.locator import Locator as Locator
from selene.core.wait import Wait as Wait
from selene.common._typing_functions import Query as Query, Command as Command
from selene.support.webdriver import WebHelper as WebHelper
from selenium.webdriver.remote.switch_to import SwitchTo as SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver as WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import Callable, Iterable, Optional, Tuple, TypeVar, Union, Any, Generic

from selene.core.entity import WaitingEntity, Element, Collection, E

class Browser(WaitingEntity['Browser']):
    def __init__(self, config: Optional[Config] = ...) -> None: ...
    def with_(
        self,
        config: Optional[Config] = None,
        *,
        # Options to customize default driver lifecycle
        driver_name: str = 'chrome',
        driver_options: Optional[BaseOptions] = None,
        driver_service: Optional[Service] = None,
        driver_remote_url: Optional[str] = None,
        hold_driver_at_exit: bool = False,
        _reset_not_alive_driver_on_get_url: bool = True,
        rebuild_not_alive_driver: bool = False,
        _driver_get_url_strategy: Callable[
            [Config], Callable[[Optional[str]], None]
        ] = ...,
        # Options to customize driver management
        build_driver_strategy: Callable[[Config], WebDriver] = ...,
        _schedule_driver_teardown_strategy: Callable[
            [Config, Callable[[], WebDriver]], None
        ] = ...,
        _teardown_driver_strategy: Callable[[Config, WebDriver], None] = ...,
        _is_driver_set_strategy: Callable[[WebDriver], bool] = ...,
        _is_driver_alive_strategy: Callable[[WebDriver], bool] = ...,
        # Managed Driver
        driver: WebDriver = ...,
        # Options to customize this config creation
        _override_driver_with_all_driver_like_options: bool = True,
        # Options to customize general Selene behavior
        # > to customize waiting logic
        timeout: float = 4,
        poll_during_waits: int = ...,  # currently fake option
        _wait_decorator: Callable[[Wait[E]], Callable[[F], F]] = lambda w: lambda f: f,
        reports_folder: Optional[str] = ...,
        _counter: itertools.count = ...,
        save_screenshot_on_failure: bool = True,
        save_page_source_on_failure: bool = True,
        last_screenshot: Optional[str] = None,
        last_page_source: Optional[str] = None,
        _save_screenshot_strategy: Callable[[Config, Optional[str]], Any] = ...,
        _save_page_source_strategy: Callable[[Config, Optional[str]], Any] = ...,
        # Options to customize web browser and elements behavior
        base_url: str = '',
        _get_base_url_on_open_with_no_args: bool = False,
        window_width: Optional[int] = None,
        window_height: Optional[int] = None,
        log_outer_html_on_failure: bool = False,
        set_value_by_js: bool = False,
        type_by_js: bool = False,
        click_by_js: bool = False,
        wait_for_no_overlap_found_by_js: bool = False,
        _match_only_visible_elements_texts: bool = True,
        _match_only_visible_elements_size: bool = False,
        _match_ignoring_case: bool = False,
        _placeholders_to_match_elements: Dict[
            Literal['exactly_one', 'zero_or_one', 'one_or_more', 'zero_or_more'], Any
        ] = cast(  # noqa
            dict, MappingProxyType({})
        ),
        selector_to_by_strategy: Callable[[str], Tuple[str, str]] = ...,
        # Etc.
        _build_wait_strategy: Callable[[Config], Callable[[E], Wait[E]]] = ...,
    ) -> Browser: ...
    @property
    def driver(self) -> WebDriver: ...
    @property
    def __raw__(self): ...
    def element(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Element: ...
    def all(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Collection: ...
    def open(self, relative_or_absolute_url: Optional[str] = ...) -> Browser: ...
    def switch_to_next_tab(self) -> Browser: ...
    def switch_to_previous_tab(self) -> Browser: ...
    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser: ...
    @property
    def switch_to(self) -> SwitchTo: ...
    def quit(self) -> None: ...
    def close(self) -> Browser: ...
