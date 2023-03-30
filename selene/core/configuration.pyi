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
from typing import Callable, Optional

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.remote.webdriver import WebDriver

from selene.common import fp
from selene.common.fp import F
from selene.core.wait import Wait, E

class Config:
    """
    all options prefixed with _ are so marked as experimental and may change in future
    """

    # Options to customize default driver lifecycle
    name: str = 'chrome'
    driver_options: Optional[BaseOptions] = None
    remote_url: Optional[str] = None
    hold_driver_at_exit: bool = False
    rebuild_dead_driver: bool = True
    # Options to customize driver management
    driver: WebDriver = (...,)  # todo: accept custom Descriptors
    driver_factory: Callable[[Config], WebDriver] = ...
    is_driver_set_strategy: Callable[[WebDriver], bool] = ...
    is_driver_alive_strategy: Callable[[WebDriver], bool] = ...
    # Options to customize this config creation
    _deep_copy_implicitly_driver_with_name: bool = True
    # Options to customize browser behavior
    base_url: str = ''
    window_width: Optional[int] = None
    window_height: Optional[int] = None
    # Options to customize browser and elements behavior
    # > to customize waiting logic
    timeout: float = 4
    poll_during_waits: int = ...  # currently fake option
    log_outer_html_on_failure: bool = False
    _wait_decorator: Callable[
        [Wait[E]], Callable[[F], F]
    ] = lambda _: fp.identity
    reports_folder: Optional[str] = ...
    _counter: itertools.count = ...
    save_screenshot_on_failure: bool = True
    save_page_source_on_failure: bool = True
    # Options to customize elements behavior
    set_value_by_js: bool = False
    type_by_js: bool = False
    click_by_js: bool = False
    wait_for_no_overlap_found_by_js: bool = False

    def __init__(
        self,
        # Options to customize default driver lifecycle
        name: str = 'chrome',
        driver_options: Optional[BaseOptions] = None,
        remote_url: Optional[str] = None,
        hold_driver_at_exit: bool = False,
        rebuild_dead_driver: bool = True,
        # Options to customize driver management
        driver: WebDriver = ...,  # todo: accept custom Descriptors
        driver_factory: Callable[[Config], WebDriver] = ...,
        is_driver_set_strategy: Callable[[WebDriver], bool] = ...,
        is_driver_alive_strategy: Callable[[WebDriver], bool] = ...,
        # Options to customize this config creation
        _deep_copy_implicitly_driver_with_name: bool = True,
        # Options to customize browser behavior
        base_url: str = '',
        window_width: Optional[int] = None,
        window_height: Optional[int] = None,
        # Options to customize browser and elements behavior
        # > to customize waiting logic
        timeout: float = 4,
        poll_during_waits: int = ...,  # currently fake option
        log_outer_html_on_failure: bool = False,
        _wait_decorator: Callable[
            [Wait[E]], Callable[[F], F]
        ] = lambda _: fp.identity,
        reports_folder: Optional[str] = ...,
        _counter: itertools.count = ...,
        save_screenshot_on_failure: bool = True,
        save_page_source_on_failure: bool = True,
        # Options to customize elements behavior
        set_value_by_js: bool = False,
        type_by_js: bool = False,
        click_by_js: bool = False,
        wait_for_no_overlap_found_by_js: bool = False,
    ): ...
    def with_(
        self,
        # Options to customize default driver lifecycle
        name: str = 'chrome',
        driver_options: Optional[BaseOptions] = None,
        remote_url: Optional[str] = None,
        hold_driver_at_exit: bool = False,
        rebuild_dead_driver: bool = True,
        # Options to customize driver management
        driver: WebDriver = ...,  # todo: accept custom Descriptors
        driver_factory: Callable[[Config], WebDriver] = ...,
        is_driver_set_strategy: Callable[[WebDriver], bool] = ...,
        is_driver_alive_strategy: Callable[[WebDriver], bool] = ...,
        # Options to customize this config creation
        _deep_copy_implicitly_driver_with_name: bool = True,
        # Options to customize browser behavior
        base_url: str = '',
        window_width: Optional[int] = None,
        window_height: Optional[int] = None,
        # Options to customize browser and elements behavior
        # > to customize waiting logic
        timeout: float = 4,
        poll_during_waits: int = ...,  # currently fake option
        log_outer_html_on_failure: bool = False,
        _wait_decorator: Callable[
            [Wait[E]], Callable[[F], F]
        ] = lambda _: fp.identity,
        reports_folder: Optional[str] = ...,
        _counter: itertools.count = ...,
        save_screenshot_on_failure: bool = True,
        save_page_source_on_failure: bool = True,
        # Options to customize elements behavior
        set_value_by_js: bool = False,
        type_by_js: bool = False,
        click_by_js: bool = False,
        wait_for_no_overlap_found_by_js: bool = False,
    ): ...
