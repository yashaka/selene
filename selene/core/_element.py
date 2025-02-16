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

import warnings
from typing_extensions import Self, Union, Tuple

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement

from selene.common._typing_functions import Command
from selene.core.configuration import Config
from selene.core._elements import All
from selene.core._elements_context import _ElementsContext
from selene.core._entity import _WaitingConfiguredEntity
from selene.core.locator import Locator


class Element(
    _ElementsContext[WebElement, WebElement, 'Element', All['Element']],
    _WaitingConfiguredEntity,
):
    def __init__(
        self,
        locator: Locator[WebElement],
        config: Config,
        **kwargs,
    ):
        _Element = kwargs.pop('_Element', self.__class__)
        _All = kwargs.pop('_All', All)
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            _All=_All,
            **kwargs,
        )

    # TODO: consider custom lazy caching (with lazy save of webelement to cache)
    #       kind of .cachable ;)

    # --- Commands --- #

    def set_value(self, value: Union[str, int]) -> Self:
        # TODO: should we move all commands like following or queries like in conditions - to separate py modules?
        # TODO: should we make them webelement based (Callable[[WebElement], None]) instead of element based?
        def fn(element: Self):
            webelement = element.locate()
            # TODO: consider to change to impl based not on clear,
            #       because clear generates post-events...
            webelement.clear()
            webelement.send_keys(str(value))

        self.wait.for_(Command(f'set value: {value}', fn))

        # TODO: consider returning self.cached, since after first successful call,
        #       all next ones should normally pass
        #       no waiting will be needed normally
        #       if yes - then we should pass fn commands to wait.for_ so the latter will return webelement to cache
        #       also it will make sense to make this behaviour configurable...
        return self

    def set(self, value: Union[str, int]) -> Self:
        """
        Sounds similar to Element.set_value(self, value), but considered to be used in broader context.
        For example, a use can say «Set gender radio to Male» but will hardly say «Set gender radio to value Male».
        Now imagine, on your project you have custom html implementation of radio buttons,
        and want to teach selene to set such radio-button controls
        – you can do this via Element.set(self, value) method,
        after monkey-patching it according to your behavior;)
        """
        return self.set_value(value)

    def type(self, text: Union[str, int]) -> Self:
        self.wait.command(
            f'type: {text}',
            lambda element: element.locate().send_keys(str(text)),
        )

        return self

    def send_keys(self, *value) -> Self:
        """
        To be used for more low level operations like «uploading files», etc.
        To simulate normal input of keys by user when typing
        - use Element.type(self, text).
        """
        self.wait.command(
            f'send keys: {value}',
            lambda element: element.locate().send_keys(*value),
        )

        return self

    def press(self, *keys) -> Self:
        self.wait.command(
            f'press keys: {keys}',
            lambda element: element.locate().send_keys(*keys),
        )

        return self

    def clear(self) -> Self:
        self.wait.command(
            'clear',
            lambda element: element.locate().clear(),
        )

        return self

    # TODO: consider support of percentage in offsets (in command.js.click too)
    def click(self, *, xoffset=0, yoffset=0) -> Self:
        """Just a normal click with optional offset"""

        def raw_click(element: Self):
            element.locate().click()

        def click_with_offset_actions(element: Self):
            actions: ActionChains = ActionChains(self.config.driver)
            webelement = element.locate()
            actions.move_to_element_with_offset(
                webelement, xoffset, yoffset
            ).click().perform()

        self.wait.for_(
            Command('click', raw_click)
            if (not xoffset and not yoffset)
            else Command(
                f'click(xoffset={xoffset},yoffset={yoffset})',
                click_with_offset_actions,
            )
        )

        return self

    # --- Deprecated --- #

    def press_enter(self) -> Self:
        warnings.warn(
            'element.press_enter() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        return self.press(Keys.ENTER)

    def press_escape(self) -> Self:
        warnings.warn(
            'element.press_escape() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        return self.press(Keys.ESCAPE)

    def press_tab(self) -> Self:
        warnings.warn(
            'element.press_tab() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        return self.press(Keys.TAB)

    def submit(self) -> Self:
        warnings.warn(
            'element.submit() is deprecated because does not make sense for mobile',
            DeprecationWarning,
        )

        self.wait.command(
            'submit',
            lambda element: element.locate().submit(),
        )

        return self

    def double_click(self) -> Self:
        warnings.warn(
            'element.double_click() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Self):
            webelement = element.locate()
            actions.double_click(webelement).perform()

        self.wait.command('double click', fn)

        return self

    def context_click(self) -> Self:
        warnings.warn(
            'element.context_click() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Self):
            webelement = element.locate()
            actions.context_click(webelement).perform()

        self.wait.command('context click', fn)

        return self

    def hover(self) -> Self:
        warnings.warn(
            'element.hover() is deprecated because will not work for mobile',
            DeprecationWarning,
        )
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Self):
            webelement = element.locate()
            actions.move_to_element(webelement).perform()

        self.wait.command('hover', fn)

        return self

    def s(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Element:
        warnings.warn(
            "consider using more explicit `element` instead: browser.element('#foo').element('.bar')",
            DeprecationWarning,
        )
        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> All[Element]:
        warnings.warn(
            "consider using `all` instead: browser.element('#foo').all('.bar')",
            DeprecationWarning,
        )
        return self.all(css_or_xpath_or_by)
