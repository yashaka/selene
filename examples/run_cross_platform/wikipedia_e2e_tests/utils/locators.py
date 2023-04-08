import typing
from typing import Optional

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.remote.webelement import WebElement

import selene
from examples.run_cross_platform import project
from selene import browser
from selene.core.locator import Locator


def is_mobile():
    return hasattr(browser.config.driver_options, 'platform_name') and (
        browser.config.driver_options.platform_name.lower()
        in ('android', 'ios')
    )


class SkippedWebElement:
    """Element that ignores all actions, returning None on any call"""

    def __getattr__(self, item):
        return lambda *args, **kwargs: None


LOCATOR_FOR_ELEMENT_TO_SKIP = Locator(
    'Element that ignores all actions',
    lambda: typing.cast(WebElement, SkippedWebElement()),
)


class By:
    def __call__(self, same=None, **kwargs):
        value = self._value_per_platform(same, **kwargs)
        if not value:
            return LOCATOR_FOR_ELEMENT_TO_SKIP

        return (
            selene.by.css(value)
            if not is_mobile()
            else (
                (AppiumBy.ID, f'{project.config.app_package}:id/{value[1:]}')
                if value.startswith('#')
                else (AppiumBy.XPATH, value)
            )
        )

    @staticmethod
    def _value_per_platform(same: Optional[str] = None, **kwargs):
        return same or (
            kwargs.get('drd') if is_mobile() else kwargs.get('web')
        )

    def id(self, same=None, **kwargs):
        value = self._value_per_platform(same, **kwargs)
        if not value:
            return LOCATOR_FOR_ELEMENT_TO_SKIP

        return (
            (AppiumBy.ID, f'{project.config.app_package}:id/{value}')
            if is_mobile()
            else f'#{value}'
        )

    # TODO: rename to caption?
    def name(self, same=None, **kwargs):
        value = self._value_per_platform(same, **kwargs)
        if not value:
            return LOCATOR_FOR_ELEMENT_TO_SKIP

        return (
            (AppiumBy.ACCESSIBILITY_ID, value)
            if is_mobile()
            else selene.by.text(value)
        )

    def text(self, same=None, **kwargs):
        value = self._value_per_platform(same, **kwargs)
        if not value:
            return LOCATOR_FOR_ELEMENT_TO_SKIP

        return selene.by.text(value)

    def partial_text(self, same=None, **kwargs):
        value = self._value_per_platform(same, **kwargs)
        if not value:
            return LOCATOR_FOR_ELEMENT_TO_SKIP

        return selene.by.partial_text(value)


by = By()
