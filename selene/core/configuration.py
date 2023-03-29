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

import atexit
import dataclasses
import itertools
import os
import re
import time
import typing
from dataclasses import dataclass, field, asdict, InitVar
from typing import Callable, Optional, Union, Tuple, List

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.options import ArgOptions, BaseOptions

from selene.common import fp
from selene.common.data_structures import persistent
from selene.common.fp import F

from selene.core.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from selene.core.wait import Wait, E


def _build_local_driver_by_name_or_remote_by_url(
    config: Config,
) -> WebDriver:
    from selenium.webdriver import (
        ChromeOptions,
        EdgeOptions,
        Chrome,
        Firefox,
        Edge,
    )

    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService

    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    from webdriver_manager.core.utils import ChromeType

    def install_and_build_chrome():
        if config.driver_options:
            if isinstance(config.driver_options, ChromeOptions):
                return Chrome(
                    service=ChromeService(
                        ChromeDriverManager(
                            chrome_type=ChromeType.GOOGLE
                        ).install()
                    ),
                    options=config.driver_options,
                )
            else:
                raise ValueError(
                    f'Default config.driver_factory («driver factory»), '
                    f'if config.name is set to "chrome", – '
                    f'expects only instance of ChromeOptions or None in config.driver_options,'
                    f'but got: {config.driver_options}'
                )
        else:
            return Chrome(
                service=ChromeService(
                    ChromeDriverManager(
                        chrome_type=ChromeType.GOOGLE
                    ).install()
                )
            )

    def install_and_build_firefox():
        return (
            Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=config.driver_options,
            )
            if config.driver_options
            else Firefox(
                service=FirefoxService(GeckoDriverManager().install())
            )
        )

    def install_and_build_edge():
        if config.driver_options:
            if isinstance(config.driver_options, EdgeOptions):
                return Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()),
                    options=config.driver_options,
                )
            else:
                raise ValueError(
                    f'Default config.driver_factory, '
                    f'if config.name is set to "edge", – '
                    f'expects only instance of EdgeOptions or None in config.driver_options,'
                    f'but got: {config.driver_options}'
                )
        else:
            return Edge(
                service=EdgeService(EdgeChromiumDriverManager().install())
            )

    def build_remote_driver():
        from selenium.webdriver import Remote

        return Remote(
            command_executor=config.remote_url,
            options=config.driver_options,
        )

    return {
        'chrome': install_and_build_chrome,
        'firefox': install_and_build_firefox,
        'edge': install_and_build_edge,
        'remote': build_remote_driver,
    }.get(config.name if not config.remote_url else 'remote', 'chrome')()


def _is_alive_driver(instance: WebDriver) -> bool:
    if instance is ... or not instance:
        return False

    try:
        return instance.title is not None  # TODO: refactor
    except Exception:  # noqa
        return False


def _is_driver_set_and_alive(instance: Optional[WebDriver]) -> bool:
    if instance is ... or not instance:
        return False

    return _is_alive_driver(instance)


class ManagedDriverDescriptor:
    def __init__(self, *, default: Optional[WebDriver] = ...):
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        config = typing.cast(Config, instance)

        driver_box = typing.cast(persistent.Box, getattr(config, self.name))
        if driver_box.value is ...:
            driver_box.value = config._build_driver()

        return driver_box.value

    def __set__(self, instance, value):
        config = typing.cast(Config, instance)

        if not hasattr(instance, self.name):
            if isinstance(value, persistent.Box):
                driver_box = value
            elif persistent._is_of_descriptor_type(value):
                driver_box = persistent.Box(self.default)
            else:
                driver_box = persistent.Box(value)

            setattr(instance, self.name, driver_box)

            atexit.register(
                lambda: (
                    driver_box.value.quit()
                    if not config.hold_browser_open
                    and _is_driver_set_and_alive(driver_box.value)
                    else None
                )
            )
        else:
            driver_box = getattr(instance, self.name)
            driver_box.value = value

            # def driver_installed_and_rebuilt_after_death():
            #     return (
            #         driver_box.value
            #         if _is_driver_set_and_alive(driver_box.value)
            #         # TODO: should we be more explicit like:
            #         # if (
            #         #     driver_box.value is not ...
            #         #     and _is_alive_driver(driver_box.value)
            #         # )
            #         else config._build_driver()
            #     )
            #
            # if (
            #     # was driver previously set via built-in driver-management logic...
            #     re.sub(' at 0x.+>$', '>', str(driver_box.value))
            #     == re.sub(
            #         ' at 0x.+>$',
            #         '>',
            #         str(driver_installed_and_rebuilt_after_death),
            #     )
            #     # and ...
            #     and _is_driver_set_and_alive(driver_box.value)
            # ):
            #     driver_box.value.quit()
            #
            # # is requested to reset driver by setting it to ... or None
            # if value is ... or value is None:
            #     driver_box.value = ...
            #     # self._driver_source = driver_installed_and_rebuilt_after_death
            # else:
            #     driver_box.value = value

    # def __delete__(self, instance):
    #     if self.driver is not ...:
    #         self.driver.quit()
    #         self.driver = ...


@persistent.dataclass
class Config:
    """
    A one cross-cutting-concern-like object to group all options
    that might influence Selene behavior depending on context.
    As option the driver instance is also considered.
    More over, this config is not just config,
    but partially manages the driver lifecycle.
    By this we definitely break SRP principle... in the name of Good:D

    All this makes it far from being a simple options data class...
    – yet kept as one «class for everything» to keep things easier to use,
    especially taking into account some historical reasons of Selene's design.
    """

    # TODO: consider allowing to provide a Descriptor as a value
    #       either explicitly like `Config(driver=HERE_DriverDescriptor(...))`
    #       or by inheritance like:
    #           class MyConfig(Config):
    #              driver: WebDriver = HERE_DriverDescriptor(...)
    #       and then `MyConfig(driver=...)` will work as expected
    driver: WebDriver = ManagedDriverDescriptor(default=...)
    """
    A driver instance. 
     
    GIVEN unset, i.e. equals to default `...`, 
    WHEN ... o_O ?
    THEN it will be set to the instance built by `config.driver_factory`.
    AND ... o_O ?
    
    GIVEN set manually to an existing driver instance,
          like: `browser.config.driver = Chrome()`
    THEN 
    
    GIVEN set manually or not
    AND `config.hold_browser_open` is set to `False` (that is default)
    WHEN the process exits
    THEN driver will be quit on exit by default.
    
    To keep its finalization on your side, set `config.hold_browser_open=True`.
    """

    driver_factory: Callable[
        [Config], WebDriver
    ] = _build_local_driver_by_name_or_remote_by_url

    # TODO: should we make it public?
    #       in fact keeping methods that do something as public in config...
    #       may confuse when comparing them to options like `hold_browser_open`
    #       and `rebuild_dead_driver` that are just boolean options...
    def _build_driver(self):
        return self.driver_factory(self)

    driver_options: Optional[BaseOptions] = None

    # TODO: should we name it driver_executor?
    #       as it's named in RemoteWebDriver constructor...
    #       or maybe driver_url?
    remote_url: Optional[str] = None

    # TODO: Consider alternative naming among:
    #           browser.config.name = 'chrome'
    #           browser.config.driver_name = 'chrome'
    #           browser.config.automation_name = 'chrome'
    # TODO: consider setting to None or ... by default, and pick up by factory any installed browser in a system
    name: str = 'chrome'
    """
    Desired name of the driver to be processed by Selene's default config.driver_factory.
    It is ignored by default config.driver_factory if config.remote_url is set.
    
    GIVEN set to any of: 'chrome', 'firefox', 'edge', 
    AND config.driver is left unset (default value is ...),
    THEN default config.driver_factory will automatically install drivers
    AND build webdriver instance for you
    AND this config will store the instance in config.driver
    """

    # TODO: consider to deprecate because might confuse in case of Appium usage
    @property
    def browser_name(self) -> str:
        return self.name

    # TODO: consider to deprecate because might confuse in case of Appium usage
    @browser_name.setter
    def browser_name(self, value: str):
        self.name = value

    # TODO: consider deprecating
    @property
    def _driver_instance(self) -> WebDriver:
        """
        Depending on whether `self.driver` is instance or instance factory (function),
        returns driver instance correspondingly.
        """
        return self.driver() if callable(self.driver) else self.driver

    # TODO: consider deprecating in favor of `hold_driver: bool = False` property
    hold_browser_open: bool = False
    """Controls whether driver will be automatically quit on process exit or not."""

    rebuild_dead_driver: bool = False
    """Controls whether driver will be automatically quit on process exit or not."""

    def __post_init__(self):
        self._register_browser_finalizer()

        # TODO: consider making private
        # TODO: do we even need them at __post_init__?
        self.last_screenshot: Optional[str] = None
        self.last_page_source: Optional[str] = None

    def _register_browser_finalizer(self):
        atexit.register(
            lambda: (
                self._driver_instance.quit()
                if not self.hold_browser_open and self._is_driver_alive
                else None
            )
        )

    @property
    def _is_driver_alive(self) -> bool:
        if self.driver is ... or not self.driver:
            return False

        try:
            return self._driver_instance.title is not None  # TODO: refactor
        except Exception:  # noqa
            return False

    timeout: float = 4
    base_url: str = ''

    set_value_by_js: bool = False
    type_by_js: bool = False
    click_by_js: bool = False
    wait_for_no_overlap_found_by_js: bool = False
    log_outer_html_on_failure: bool = False

    window_width: Optional[int] = None
    window_height: Optional[int] = None

    # TODO: better name? now technically it's not a decorator but decorator_builder...
    # or decorator_factory...
    # yet in python they call it just «decorator with args» or «decorator with params»
    # so technically we are correct naming it simply _wait_decorator
    # by type hint end users yet will see the real signature
    # and hence guess its «builder-like» nature
    # yet... should we for verbosity distinguish options
    # that a decorator factories from options that are simple decorators?
    # maybe better time to decide on this will be once we have more such options :p
    _wait_decorator: Callable[
        [Wait[E]], Callable[[F], F]
    ] = lambda _: fp.identity

    hook_wait_failure: Optional[Callable[[TimeoutException], Exception]] = None
    '''
    A handler for all exceptions, thrown on failed waiting for timeout.
    Should process the original exception and rethrow it or the modified one.

    TODO: why we name it as hook_* why not handle_* ?
          what would be proper style?
    '''

    poll_during_waits: int = 100
    """
    a fake option, not currently used in Selene waiting:)
    """

    reports_folder: str = os.path.join(
        os.path.expanduser('~'),
        '.selene',
        'screenshots',
        str(round(time.time() * 1000)),
    )
    save_screenshot_on_failure: bool = True
    save_page_source_on_failure: bool = True
    _counter: itertools.count = itertools.count(
        start=int(round(time.time() * 1000))
    )
    """
    A counter, currently used for incrementing screenshot names
    """

    def with_(self, /, **config_as_kwargs) -> Config:
        return persistent.replace(self, **config_as_kwargs)

    def _generate_filename(self, prefix='', suffix=''):
        path = self.reports_folder
        next_id = next(self._counter)
        filename = f'{prefix}{next_id}{suffix}'
        file = os.path.join(path, f'{filename}')

        folder = os.path.dirname(file)
        if not os.path.exists(folder) and folder:
            os.makedirs(folder)

        return file

    # TODO: consider moving this injection to the WaitingEntity.wait method to build Wait object instead of config.wait
    def _inject_screenshot_and_page_source_pre_hooks(self, hook):
        # todo: consider moving hooks to class methods accepting config as argument
        #       or refactor somehow to eliminate all times defining hook fns
        def save_and_log_screenshot(error: TimeoutException) -> Exception:
            from selene.support.webdriver import WebHelper

            path = WebHelper(self.driver).save_screenshot(
                self._generate_filename(suffix='.png')
            )
            self.last_screenshot = path
            return TimeoutException(
                error.msg
                + f'''
Screenshot: file://{path}'''
            )

        def save_and_log_page_source(error: TimeoutException) -> Exception:
            filename = (
                # TODO: this dependency to last_screenshot might lead to code,
                #       when wrong screenshot name is taken
                self.last_screenshot.replace('.png', '.html')
                if getattr(self, 'last_screenshot', None)
                else self._generate_filename(suffix='.html')
            )
            from selene.support.webdriver import WebHelper

            path = WebHelper(self.driver).save_page_source(filename)
            self.last_page_source = path
            return TimeoutException(error.msg + f'\nPageSource: file://{path}')

        return fp.pipe(
            save_and_log_screenshot
            if self.save_screenshot_on_failure
            else None,
            save_and_log_page_source
            if self.save_page_source_on_failure
            else None,
            hook,
        )

    # TODO: we definitely not need it inside something called Config, especially "base interface like config
    def wait(self, entity):
        hook = self._inject_screenshot_and_page_source_pre_hooks(
            self.hook_wait_failure
        )
        return Wait(
            entity,
            at_most=self.timeout,
            or_fail_with=hook,
            _decorator=self._wait_decorator,
        )
