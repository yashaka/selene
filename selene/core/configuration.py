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

from __future__ import annotations

import atexit
import inspect
import itertools
import os
import time
import typing
import warnings
from typing import Callable, Optional

from selenium.webdriver.common.options import BaseOptions

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


class ManagedDriverDescriptor:
    def __init__(self, *, default: Optional[WebDriver] = ...):
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        config = typing.cast(Config, instance)
        # Below...
        # we can't access driver via config.driver explicitly
        # or implicitly by calling other config.* methods,
        # because it will lead to recursion!!!

        driver_box = typing.cast(
            persistent.Box[WebDriver], getattr(config, self.name)
        )
        if driver_box.value is ... or (
            config.rebuild_dead_driver
            and not callable(driver_box.value)  # TODO: consider deprecating
            and not config.is_driver_alive_strategy(driver_box.value)
        ):
            driver = config.driver_factory(config)
            driver_box.value = driver
            config._schedule_driver_teardown_strategy(config, lambda: driver)

        value = driver_box.value
        if callable(value):
            warnings.warn(
                'Providing driver as callable might be deprecated in future. '
                'Consider customizing driver management '
                'via other config.* options',
                FutureWarning,
            )
            return value()

        return value

    def __set__(self, instance, value):
        config = typing.cast(Config, instance)

        if not hasattr(instance, self.name):
            # setting this attribute for the first time,
            # probably (TODO: probably or for sure?) in the __init__ method

            if isinstance(value, persistent.Box):
                # it's a boxed value,
                # probably passed implicitly via `persistent.replace`
                driver_box = value
            elif inspect.isdatadescriptor(value):
                # the value happened to be a descriptor
                # it's either object of this descriptor type (`type(self)`)
                # or custom provided descriptor during init new object
                if type(value) is type(self):
                    # we are processing this `self` descriptor as value
                    # so, instead of value, we should store `self.default`
                    driver_box = persistent.Box(self.default)
                else:
                    # somebody decided to provide his own descriptor object
                    # Heh:) It was a good try, but no ;P
                    raise TypeError(
                        'Providing custom descriptor objects on init '
                        'to customize driver management is not supported, '
                        'because it would be too limited... '
                        'You would be able to provide it only on init,'
                        'and use it only via attribute access,'
                        'without possibility to override value with `persistent.replace` '
                        'or `config.with_(**overrides)`. '
                        'If you want to use custom descriptor, '
                        'you have to subclass Config and provide your descriptor object'
                        'on class attributes definition level.'
                    )  # TODO: cover with tests
            else:
                # setting WebDriver instance directly on init
                driver_box = persistent.Box(value)

                if not callable(value):
                    config._schedule_driver_teardown_strategy(
                        config, lambda: value
                    )

            setattr(instance, self.name, driver_box)
        else:
            # setting WebDriver instance after init
            driver_box = getattr(instance, self.name)
            driver_box.value = value

            # TODO: should not we check value set above,
            #       wasn't the same as was in driver_box.value before?
            #       if yes, we might not want to add one more atexit handler
            if not callable(value):
                config._schedule_driver_teardown_strategy(
                    config, lambda: value
                )


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

    # TODO: should we rename driver_factory to build_driver_strategy
    #       for compliance with other *_strategy options?
    #       especially with teardown_driver_strategy...
    #       from other point of view...
    #       this option is something bigger than *_strategy
    #       because it's based on the whole config instance,
    #       not just pure «unboxed» WebDriver instance
    driver_factory: Callable[
        [Config], WebDriver
    ] = _build_local_driver_by_name_or_remote_by_url
    """
    A factory to build a driver instance based on this config instance.
    The driver built with this factory will be available via `config.driver`.
    Hence, you can't use `config.driver` directly inside this factory,
    because it may lead to recursion.

    The default factory builds:
    * either a local driver by value specified in `config.browser_name`
    * or remote driver by value specified in `config.remote_url`.
    """

    # TODO: isn't this option too much?
    #       having it, we have to keep driver descriptor definition
    #       after this option definition,
    #       that is pretty tightly coupled...
    #       heh, but maybe we definitely have to keep it defined
    #       after all "strategy" options...
    # Currently we don't use the power of get_driver being callable...
    # It would work even if we pass simply driver instance...
    # Should we simplify things? Or keep it as is with get_driver?
    _schedule_driver_teardown_strategy: Callable[
        [Config, Callable[[], WebDriver]],
        None,
    ] = lambda config, get_driver: atexit.register(  # TODO: get_driver or simply driver?
        lambda: config._teardown_driver_strategy(config, get_driver())
    )

    _teardown_driver_strategy: Callable[
        [Config, WebDriver], None
    ] = lambda config, driver: (
        driver.quit()
        if not config.hold_driver_at_exit
        and config.is_driver_set_strategy(driver)
        and config.is_driver_alive_strategy(driver)
        else None
    )

    is_driver_set_strategy: Callable[[WebDriver], bool] = lambda driver: (
        driver is not ... and driver is not None
    )

    is_driver_alive_strategy: Callable[[WebDriver], bool] = lambda driver: (
        driver.service.process is not None
        and driver.service.process.poll() is None
    )

    driver_options: Optional[BaseOptions] = None

    # TODO: should we name it driver_executor?
    #       as it's named in RemoteWebDriver constructor...
    #       or maybe driver_url?
    remote_url: Optional[str] = None

    # TODO: Consider alternative naming among:
    #           browser.config.name = 'chrome'
    #           browser.config.driver_name = 'chrome'
    #           browser.config.automation_name = 'chrome'
    #       Maybe driver_name is the best one?
    #       * TODO: Check what it actually is set under driver.name for appium and remote cases
    # TODO: consider setting to None or ... by default, and pick up by factory any installed browser in a system
    name: str = 'chrome'
    """
    Desired name of the driver to be processed by Selene's default config.driver_factory.
    It is ignored by default `config.driver_factory` if `config.remote_url` is set.

    GIVEN set to any of: 'chrome', 'firefox', 'edge',
    AND config.driver is left unset (default value is ...),
    THEN default config.driver_factory will automatically install drivers
    AND build webdriver instance for you
    AND this config will store the instance in config.driver
    """

    # TODO: finalize the name of this option and consider making public
    _deep_copy_implicitly_driver_with_name: bool = True
    """
    Controls whether driver will be deep copied with config.name
    when customizing config via `config.with_(**options)`.

    Examples:
        Building 2 drivers with implicit deep copy of driver storage:

        >>> chrome_config = Config(
        >>>     name='chrome',
        >>>     timeout=10.0,
        >>>     base_url='https://autotest.how',
        >>> )
        >>> chrome = chrome_config.driver
        >>> firefox_config = chrome_config.with_(name='firefox')
        >>> firefox = firefox_config.driver
        >>> assert firefox is not chrome

        Building 2 drivers with explicit deep copy of driver storage [1]:

        >>> chrome_config = Config(
        >>>     name='chrome',
        >>>     timeout=10.0,
        >>>     base_url='https://autotest.how',
        >>>     _deep_copy_implicitly_driver_with_name=False,
        >>> )
        >>> chrome = chrome_config.driver
        >>> firefox_config = chrome_config.with_(name='firefox', driver=...)
        >>> firefox = firefox_config.driver
        >>> assert firefox is not chrome

        Building 2 drivers with explicit deep copy of driver storage [2]:

        >>> chrome_config = Config(
        >>>     name='chrome',
        >>>     timeout=10.0,
        >>>     base_url='https://autotest.how',
        >>> )
        >>> chrome_config._deep_copy_implicitly_driver_with_name = False
        >>> chrome = chrome_config.driver
        >>> firefox_config = chrome_config.with_(name='firefox', driver=...)
        >>> firefox = firefox_config.driver
        >>> assert firefox is not chrome

        Building 1 driver because driver storage was not copied:

        >>> chrome_config = Config(
        >>>     name='chrome',
        >>>     timeout=10.0,
        >>>     base_url='https://autotest.how',
        >>> )
        >>> chrome_config._deep_copy_implicitly_driver_with_name = False
        >>> chrome = chrome_config.driver
        >>> firefox_config = chrome_config.with_(name='firefox')
        >>> firefox = firefox_config.driver
        >>> assert firefox is chrome  # o_O ;)
    """

    # TODO: consider to deprecate because might confuse in case of Appium usage
    @property
    def browser_name(self) -> str:
        return self.name

    # TODO: consider to deprecate because might confuse in case of Appium usage
    @browser_name.setter
    def browser_name(self, value: str):
        self.name = value

    # TODO: do we need it?
    # quit_last_driver_on_reset: bool = False
    # """Controls whether driver will be automatically quit at reset of config.driver"""

    hold_driver_at_exit: bool = False
    """
    Controls whether driver will be automatically quit at process exit or not.

    Will not take much effect for 4.5.0 < selenium versions <= 4.8.3 < ?.?.?,
    Because for some reason, Selenium of such versions kills driver by himself,
    regardless of what Selene thinks about it:D
    """

    # TODO: deprecate
    @property
    def hold_browser_open(self) -> bool:
        return self.hold_driver_at_exit

    # TODO: deprecate
    @hold_browser_open.setter
    def hold_browser_open(self, value: bool):
        self.hold_driver_at_exit = value

    rebuild_dead_driver: bool = True
    """Controls whether driver should be automatically rebuilt if it was quit or crashed."""

    # TODO: consider allowing to provide a Descriptor as a value
    #       by inheritance like:
    #           class MyConfig(Config):
    #              driver: WebDriver = HERE_DriverDescriptor(...)
    #       and then `MyConfig(driver=...)` will work as expected
    # TODO: should we accept a callable here to bypass driver_factory logic?
    #       currently we do... we don't show it explicitly...
    #       but the valid type is Union[WebDriver, Callable[[], WebDriver]]
    #       so... should we do it?
    #       why not just use driver_factory for same?
    #       there is the difference though...
    #       the driver factory is only used as a driver builder,
    #       it does not cover other stages of driver lifecycle,
    #       like teardown...
    #       but if we provide a callable instance to driver,
    #       then it will just substitute the whole lifecycle
    driver: WebDriver = ManagedDriverDescriptor(default=...)
    """
    A driver instance with lifecycle managed by this config special options
    (TODO: specify these options...),
    depending on their values and customization of this attribute.

    GIVEN unset, i.e. equals to default `...`,
    WHEN accessed first time (e.g. via config.driver)
    THEN it will be set to the instance built by `config.driver_factory`.

    GIVEN set manually to an existing driver instance,
          like: `config.driver = Chrome()`
    THEN it will be reused at it is on any next access
    WHEN reset to `...`
    THEN will be rebuilt by `config.driver_factory`

    GIVEN set manually to a callable that returns WebDriver instance
          (currently marked with FutureWarning, so might be deprecated)
    WHEN accessed fist time
    AND any next time
    THEN will call the callable and return the result

    GIVEN unset or set manually to not callable
    AND `config.hold_driver_at_exit` is set to `False` (that is default)
    WHEN the process exits
    THEN driver will be quit.
    """

    def __post_init__(self):
        # TODO: consider making private
        # TODO: do we even need them at __post_init__?
        self.last_screenshot: Optional[str] = None
        self.last_page_source: Optional[str] = None

    base_url: str = ''
    window_width: Optional[int] = None
    window_height: Optional[int] = None

    timeout: float = 4
    log_outer_html_on_failure: bool = False
    set_value_by_js: bool = False
    type_by_js: bool = False
    click_by_js: bool = False
    wait_for_no_overlap_found_by_js: bool = False

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

    def with_(self, **config_as_kwargs) -> Config:
        """

        Parameters:
            **config_as_kwargs:
                options to override in the new config.

                If `name` is among them, and `driver` is not among them,
                and `self._deep_copy_implicitly_driver_with_name` is True,
                then `driver` will be implicitly added to the options to override,
                i.e. `with_(name='firefox')` will be equivalent
                to `with_(name='firefox', driver=...)`.
                The latter gives a readable and concise shortcut
                to spawn more than one browser:

                >>> config = Config(timeout=10.0, base_url='https://autotest.how')
                >>> chrome = config.driver  # chrome is default browser
                >>> firefox_config = config.with_(name='firefox')
                >>> firefox = firefox_config.driver
                >>> edge_config = config.with_(name='edge')
                >>> edge = edge_config.driver


        Returns:
            a new config with overridden options that were specified as arguments.

            All other config options will be shallow-copied
            from the current config.
            Those other options that are of immutable types,
            like `int` – will be also copied by reference,
            i.e. in a truly shallow way.
        """
        options = (
            {'driver': ..., **config_as_kwargs}
            if (
                self._deep_copy_implicitly_driver_with_name
                and 'name' in config_as_kwargs
                and 'driver' not in config_as_kwargs
            )
            else config_as_kwargs
        )
        return persistent.replace(self, **options)

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
    #       consider refactor to wait_factory as configurable config property
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
