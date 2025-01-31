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

from typing_extensions import (
    cast,
    TypeVar,
    Callable,
    override,
    Optional,
    Sequence,
    Tuple,
)

from selene.core.configuration import Config
from selene.core.locator import Locator

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


class _SkippedAppiumElement:
    """Element that ignores all actions, returning None on any call"""

    def __getattr__(self, item):
        return lambda *args, **kwargs: None


class _SkippedAppiumElements:
    """Element that ignores all actions, returning None on any call"""

    def __getattr__(self, item):
        return lambda *args, **kwargs: None


LOCATOR_FOR_ELEMENT_TO_SKIP = Locator(
    'Element that ignores all actions',
    lambda: cast(AppiumElement, _SkippedAppiumElement()),
)


LOCATOR_FOR_ELEMENTS_TO_SKIP = Locator(
    'Element that ignores all actions',
    lambda: cast(Sequence[AppiumElement], _SkippedAppiumElements()),
)


T = TypeVar('T')


class NoneWiseLocator(Locator[T]):
    # def __init__(self, description: str, locate: Callable[[], T]):
    #     self._description = description
    #     self._locate = locate

    @override
    def __call__(self) -> T:
        located = self._locate()
        return located if located is not None else cast(T, _SkippedAppiumElement())

    # def __str__(self):
    #     return self._description


class PlatformWiseByLocator(Locator[T]):
    def __init__(
        self,
        description: Callable[[Tuple[str, str]], str],
        *,
        search: Callable,
        selector_or_by_platform,
        config: Config,
    ):
        self._config = config
        self._bys_per_platform = selector_or_by_platform

        def locate():
            by = config._selector_or_by_to_by(
                selector_or_by_platform.get(self._current_platform_name)
            )
            return search(by) if by is not None else cast(T, _SkippedAppiumElement())

        super().__init__(
            lambda: description(
                config._selector_or_by_to_by(
                    selector_or_by_platform.get(self._current_platform_name)
                )
            ),
            locate,
        )

    @property
    def _current_platform_name(self):
        return self._config.driver.capabilities.get('platformName', '').lower()
