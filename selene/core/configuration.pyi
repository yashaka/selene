# MIT License
#
# Copyright (c) 2015-2023 Iakiv Kramarenko
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
import itertools
from typing import Callable, Optional, Any, Union

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.remote.webdriver import WebDriver

from selene.common.fp import F
from selene.core.wait import Wait, E

class _DriverStrategiesExecutor:
    def __init__(self, config: Config): ...
    @property
    def driver_instance(self) -> Union[Optional[WebDriver], ...]: ...  # type: ignore
    @property
    def is_driver_managed(self) -> bool: ...
    def build_driver(self) -> WebDriver: ...
    @property
    def is_driver_set(self) -> bool: ...
    @property
    def is_driver_alive(self) -> bool: ...
    @property
    def teardown(self) -> Callable[[WebDriver], None]: ...
    def schedule_teardown(self, get_driver: Callable[[], WebDriver]) -> None: ...
    def get_url(self, url: Optional[str] = None) -> None: ...
    def save_screenshot(self, path: Optional[str] = None) -> Any: ...
    def save_page_source(self, path: Optional[str] = None) -> Any: ...

class Config:
    """
    all options prefixed with _ are so marked as experimental and may change in future
    """

    # Options to customize default driver lifecycle
    driver_name: Optional[str] = None
    driver_options: Optional[BaseOptions] = None
    driver_service: Optional[Service] = None
    driver_remote_url: Optional[str] = None
    hold_driver_at_exit: bool = False
    _reset_not_alive_driver_on_get_url: bool = True
    rebuild_not_alive_driver: bool = False
    _driver_get_url_strategy: Callable[[Config], Callable[[Optional[str]], None]] = ...
    # Options to customize driver management
    build_driver_strategy: Callable[[Config], WebDriver] = ...
    _schedule_driver_teardown_strategy: Callable[
        [Config, Callable[[], WebDriver]], None
    ] = ...
    _teardown_driver_strategy: Callable[[Config, WebDriver], None] = ...
    _is_driver_set_strategy: Callable[[WebDriver], bool] = ...
    _is_driver_alive_strategy: Callable[[WebDriver], bool] = ...
    # Managed Driver
    driver: WebDriver = ...
    # Options to customize this config creation
    _override_driver_with_all_driver_like_options: bool = True
    # Options to customize general Selene behavior
    # > to customize waiting logic
    timeout: float = 4
    poll_during_waits: int = ...  # currently fake option
    _wait_decorator: Callable[[Wait[E]], Callable[[F], F]] = lambda w: lambda f: f
    reports_folder: Optional[str] = ...
    _counter: itertools.count = ...
    save_screenshot_on_failure: bool = True
    save_page_source_on_failure: bool = True
    last_screenshot: Optional[str] = None
    last_page_source: Optional[str] = None
    _save_screenshot_strategy: Callable[[Config, Optional[str]], Any] = ...
    _save_page_source_strategy: Callable[[Config, Optional[str]], Any] = ...
    # Options to customize web browser and elements behavior
    base_url: str = ''
    _get_base_url_on_open_with_no_args: bool = False
    window_width: Optional[int] = None
    window_height: Optional[int] = None
    log_outer_html_on_failure: bool = False
    set_value_by_js: bool = False
    type_by_js: bool = False
    click_by_js: bool = False
    wait_for_no_overlap_found_by_js: bool = False
    # Etc.
    _build_wait_strategy: Callable[[Config], Callable[[E], Wait[E]]] = ...
    _executor: _DriverStrategiesExecutor = ...

    def __init__(
        self,
        *,
        # Options to customize default driver lifecycle
        driver_name: Optional[str] = None,
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
        # Etc.
        _build_wait_strategy: Callable[[Config], Callable[[E], Wait[E]]] = ...,
    ): ...
    def with_(
        self,
        *,
        # Options to customize default driver lifecycle
        driver_name: Optional[str] = None,
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
        # Etc.
        _build_wait_strategy: Callable[[Config], Callable[[E], Wait[E]]] = ...,
    ): ...
