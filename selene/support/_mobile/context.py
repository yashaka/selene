# MIT License
#
# Copyright (c) 2015 Iakiv Kramarenko
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

from typing_extensions import Optional, Union, Tuple, cast

from selene.support._mobile.elements import Element, AllElements
from selene.support._mobile.locators import (
    LOCATOR_FOR_ELEMENT_TO_SKIP,
    PlatformWiseByLocator,
    LOCATOR_FOR_ELEMENTS_TO_SKIP,
)

try:
    from appium import webdriver
    from appium.webdriver import WebElement as AppiumElement
except ImportError as error:
    raise ImportError(
        'Appium-Python-Client is not installed, '
        'run `pip install Appium-Python-Client`,'
        'or add and install dependency '
        'with your favorite dependency manager like poetry: '
        '`poetry add Appium-Python-Client`'
    ) from error

from selene.core._actions import _Actions
from selene.core.configuration import Config
from selene.core.entity import WaitingEntity
from selene.core.locator import Locator


class Device(WaitingEntity['Device']):
    def __init__(self, config: Optional[Config] = None):
        config = Config() if config is None else config
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Device:
        return (
            Device(config) if config else Device(self.config.with_(**config_as_kwargs))
        )

    def __str__(self):
        return 'device'

    # todo: consider not just building driver but also adjust its size according to config
    @property
    def driver(self) -> webdriver.Remote:
        return cast(webdriver.Remote, self.config.driver)

    # TODO: consider making it callable (self.__call__() to be shortcut to self.__raw__ ...)

    @property
    def __raw__(self) -> webdriver.Remote:
        return cast(webdriver.Remote, self.config.driver)

    @property
    def _actions(self) -> _Actions:
        return _Actions(self.config)

    def _is_android_or_ios(self):
        return hasattr(self.config.driver_options, 'platform_name') and (
            self.config.driver_options.platform_name.lower() in ('android', 'ios')
        )

    def _value_per_current_platform(
        self,
        *,
        same: Optional[str] = None,
        or_per_platform: Optional[dict] = None,
    ):
        if or_per_platform is None:
            or_per_platform = {}
        return same or (
            or_per_platform.get('drd')
            if self._is_android_or_ios()
            else or_per_platform.get('web')
        )

    # --- Element builders --- #

    # TODO: consider @overload to have more specific signature variations
    # TODO: consider None by default,
    #       and *args, **kwargs to be able to pass custom things
    #       to be processed by config.location_strategy
    #       and by default process none as "element to skip all actions on it"
    def element(
        self,
        selector_or_by_or_locator: Union[str, Tuple[str, str], Locator, None] = None,
        /,
        **selector_or_by_per_platform,
    ) -> Element:
        if selector_or_by_or_locator is None and not selector_or_by_per_platform:
            return Element(LOCATOR_FOR_ELEMENT_TO_SKIP, self.config)

        if isinstance(selector_or_by_or_locator, Locator):
            if selector_or_by_per_platform:
                raise ValueError(
                    'You cannot pass both Locator and selector_or_by_per_platform'
                )
            return Element(selector_or_by_or_locator, self.config)

        # TODO: should not we apply translation in a more lazy way, based on config?
        selector_or_by_per_platform = {
            'android': selector_or_by_per_platform.get(
                'android',
                selector_or_by_per_platform.get('drd', selector_or_by_or_locator),
            ),
            'ios': selector_or_by_per_platform.get('ios', selector_or_by_or_locator),
        }

        # todo: do we need by_to_locator_strategy?
        return Element(
            PlatformWiseByLocator(
                lambda by: f'{self}.element({by})',
                search=lambda by: self.driver.find_element(*by),
                selector_or_by_platform=selector_or_by_per_platform,
                config=self.config,
            ),
            self.config,
        )

        # return Element(
        #     Locator(f'{self}.element({by})', lambda: self.driver.find_element(*by)),
        #     self.config,
        # )

    def all(
        self,
        selector_or_by_or_locator: Union[str, Tuple[str, str], Locator, None] = None,
        /,
        **selector_or_by_per_platform,
    ) -> AllElements:
        # if isinstance(selector_or_by_or_locator, Locator):
        #     return AllElements(selector_or_by_or_locator, self.config)
        #
        # by = self.config._selector_or_by_to_by(selector_or_by_or_locator)
        if selector_or_by_or_locator is None and not selector_or_by_per_platform:
            return AllElements(LOCATOR_FOR_ELEMENTS_TO_SKIP, self.config)

        if isinstance(selector_or_by_or_locator, Locator):
            if selector_or_by_per_platform:
                raise ValueError(
                    'You cannot pass both Locator and selector_or_by_per_platform'
                )
            return AllElements(selector_or_by_or_locator, self.config)

        # TODO: should not we apply translation in a more lazy way, based on config?
        selector_or_by_per_platform = {
            'android': selector_or_by_per_platform.get(
                'android',
                selector_or_by_per_platform.get('drd', selector_or_by_or_locator),
            ),
            'ios': selector_or_by_per_platform.get('ios', selector_or_by_or_locator),
        }

        # todo: do we need by_to_locator_strategy?
        return AllElements(
            PlatformWiseByLocator(
                lambda by: f'{self}.all({by})',
                search=lambda by: self.driver.find_elements(*by),
                selector_or_by_platform=selector_or_by_per_platform,
                config=self.config,
            ),
            self.config,
        )

        # return AllElements(
        #     Locator(f'{self}.all({by})', lambda: self.driver.find_elements(*by)),
        #     self.config,
        # )

    # --- High Level Commands--- #

    # # TODO: do we need it as part of a most general search context?
    # def open(self, relative_or_absolute_url: Optional[str] = None) -> Device:
    #     # TODO: should we keep it less pretty but more KISS? like:
    #     # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
    #     self.config._executor.get_url(relative_or_absolute_url)
    #
    #     return self
