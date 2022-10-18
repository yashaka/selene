from __future__ import annotations

import atexit
import re
import warnings
from dataclasses import field
from typing import Callable, Union, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from selene.core.configuration import Config as BaseConfig
from selene.core.entity import Browser


class Config(BaseConfig):
    _driver: WebDriver = field(default=..., init=False, repr=False)
    _driver_source: Callable[[], WebDriver] = field(
        default=..., init=False, repr=False
    )

    @property
    def driver(self) -> WebDriver:
        self._driver = self._driver_source()
        return self._driver

    @driver.setter
    def driver(self, value: Union[WebDriver, Callable[[], WebDriver]]):
        def ensure_installed_and_built_when_not_alive():
            return (
                self._driver
                if (self._driver is not ... and self._is_browser_alive)
                else _install_and_build_driver(self.browser_name)
            )

        if (
            # driver was previously set via built-in driver-management logic
            re.sub(' at 0x.+>$', '>', str(self._driver_source))
            == re.sub(
                ' at 0x.+>$',
                '>',
                str(ensure_installed_and_built_when_not_alive),
            )
            # and ...
            and self._driver is not ...
            and self._is_browser_alive
        ):
            self._driver.quit()

        if value is ... or value is None:
            self._driver = ...
            self._driver_source = ensure_installed_and_built_when_not_alive
        elif callable(value):
            self._driver = ...
            self._driver_source = value
        else:
            self._driver = value
            self._driver_source = lambda: value

        atexit.register(
            lambda: (
                self.driver.quit()
                if not self.hold_browser_open
                and self._driver is not ...
                and self._is_browser_alive
                else None
            )
        )

    def get_or_create_driver(self) -> WebDriver:
        warnings.warn(
            'config.get_or_create_driver is deprecated, use config.driver instead',
            DeprecationWarning,
        )
        return self.driver

    def _reset_driver_source(self):
        """
        set default value (...) to the self.driver and so to the self._driver
        Hence, by this – also resetting self._driver_source,
        i.e. returning its original «automatically managed by Selene» version

        TODO: should we make this method public?
              currently the official way to reset driver source for the user
              is `browser.config.driver = ...`
              wouldn't it be better to allow him to do:
              is `browser.config.reset_driver_source()`
              ?
        """
        self.driver = ...

    def reset_driver(self):  # noqa
        warnings.warn(
            'selene.browser.config.reset_driver is deprecated '
            'in favor of `config.driver = ...`',
            DeprecationWarning,
        )
        self.driver = ...

    @property
    def _is_browser_alive(self) -> bool:
        if self._driver is ...:
            # raise _SeleneError('the driver has not been sourced yet at config')
            warnings.warn(
                'The driver has not been sourced yet at config, '
                'but asked for being alive. '
                'There might be a situation when driver is already created '
                'and so alive but passed to config via callable '
                'and not sourced yet at config...'
            )
            return False

        try:
            return self._driver.title is not None
        except Exception:  # noqa
            return False

    def __post_init__(self):
        # TODO: consider making private
        self.last_screenshot: Optional[str] = None
        self.last_page_source: Optional[str] = None


def _install_and_build_driver(browser_name):
    # todo: do we need here pass self.desired_capabilities too?

    from selenium.webdriver import ChromeOptions, Chrome, Firefox, Edge
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from webdriver_manager.core.utils import ChromeType

    def get_chrome():
        return Chrome(
            service=ChromeService(
                ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            ),
            options=ChromeOptions(),
        )

    def get_firefox():
        return Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def get_edge():
        return Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

    return {
        'chrome': get_chrome,
        'firefox': get_firefox,
        'edge': get_edge,
    }.get(browser_name)()


config = Config()
browser = Browser(config)
