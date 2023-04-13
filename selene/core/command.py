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
import sys
from typing import Union, Optional

import typing
from selenium.webdriver import Keys

from selene.core.entity import Element, Collection, Browser
from selene.core.wait import Command
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput


def save_screenshot(path: Optional[str] = None) -> Command[Browser]:
    command: Command[Browser] = Command(
        'save screenshot',
        lambda browser: browser.config._save_screenshot_strategy(browser.config, path),
    )

    if isinstance(path, Browser):
        # somebody passed command as `.perform(command.save_screenshot)`
        # not as `.perform(command.save_screenshot())`
        browser = path
        command.__call__(browser)

    return command


def save_page_source(path: Optional[str] = None) -> Command[Browser]:
    command: Command[Browser] = Command(
        'save page source',
        lambda browser: browser.config._save_page_source_strategy(browser.config, path),
    )

    if isinstance(path, Browser):
        # somebody passed command as `.perform(command.save_screenshot)`
        # not as `.perform(command.save_screenshot())`
        browser = path
        command.__call__(browser)

    return command


select_all: Command[Element] = Command(
    'select all by ctrl+a or cmd+a for mac',
    lambda element: typing.cast(Element, element)
    .locate()
    .send_keys(
        (Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL) + 'a' + Keys.NULL,
    ),
)


# TODO: can we make it work for both mobile and web?
#       should we selectively choose proper interaction.POINTER_TOUCH below?
def _long_press(duration=1.0):
    def func(element: Element):
        located_element = element.locate()
        driver = element.config.driver
        actions: ActionChains = ActionChains(driver)

        actions.w3c_actions = ActionBuilder(
            driver, mouse=PointerInput(interaction.POINTER_TOUCH, 'touch')
        )
        (
            actions.w3c_actions.pointer_action.move_to(located_element)
            .pointer_down()
            .pause(duration)
            .release()
        )
        actions.perform()

    command = Command(f'long press with duration={duration}', func)

    if isinstance(duration, Element):
        # somebody passed command as `.perform(command.long_press)`
        # not as `.perform(command.long_press())`
        # TODO: refactor to really allow such use case without conflicts on types
        element = duration
        command.__call__(element)

    return command


class js:  # pylint: disable=invalid-name
    @staticmethod
    def set_value(value: Union[str, int]) -> Command[Element]:
        def func(element: Element):
            element.execute_script(
                """
                var text = arguments[0];
                var maxlength = element.getAttribute('maxlength') === null
                    ? -1
                    : parseInt(element.getAttribute('maxlength'));
                element.value = maxlength === -1
                    ? text
                    : text.length <= maxlength
                        ? text
                        : text.substring(0, maxlength);
                return null;
                """,
                str(value),
            )

        return Command(f'set value by js: {value}', func)

    @staticmethod
    def type(keys: Union[str, int]) -> Command[Element]:
        def func(element: Element):
            element.execute_script(
                """
                textToAppend = arguments[0];
                var value = element.value || '';
                var text = value + textToAppend;
                var maxlength = element.getAttribute('maxlength') === null
                    ? -1
                    : parseInt(element.getAttribute('maxlength'));
                element.value = maxlength === -1
                    ? text
                    : text.length <= maxlength
                        ? text
                        : text.substring(0, maxlength);
                return null;
                """,
                str(keys),
            )

        return Command(f'set value by js: {keys}', func)

    scroll_into_view: Command[Element] = Command(
        'scroll into view',
        lambda element: element.execute_script('element.scrollIntoView(true)'),
    )

    click: Command[Element] = Command(
        'click',
        # TODO: should we process collections too? i.e. click through all elements?
        lambda element: element.execute_script('element.click()'),
    )

    clear_local_storage: Command[Browser] = Command(
        'clear local storage',
        lambda browser: browser.driver.execute_script('window.localStorage.clear()'),
    )

    clear_session_storage: Command[Browser] = Command(
        'clear local storage',
        lambda browser: browser.driver.execute_script('window.sessionStorage.clear()'),
    )

    remove: Command[Union[Element, Collection]] = Command(
        'remove',
        lambda entity: (
            entity.execute_script('element.remove()')
            if not hasattr(entity, '__iter__')
            else [element.execute_script('element.remove()') for element in entity]
        ),
    )

    @staticmethod
    def set_style_property(name: str, value: Union[str, int]) -> Command[Element]:
        return Command(
            f'set element.style.{name}="{value}"',
            lambda entity: (
                entity.execute_script(f'element.style.{name}="{value}"')
                if not hasattr(entity, '__iter__')
                else [
                    element.execute_script(f'element.style.{name}="{value}"')
                    for element in entity
                ]
            ),
        )

    set_style_display_to_none: Command[Union[Element, Collection]] = Command(
        'set element.style.display="none"',
        lambda entity: (
            entity.execute_script('element.style.display="none"')
            if not hasattr(entity, '__iter__')
            else [
                element.execute_script('element.style.display="none"')
                for element in entity
            ]
        ),
    )

    set_style_display_to_block: Command[Union[Element, Collection]] = Command(
        'set element.style.display="block"',
        lambda entity: (
            entity.execute_script('element.style.display="block"')
            if not hasattr(entity, '__iter__')
            else [
                element.execute_script('element.style.display="block"')
                for element in entity
            ]
        ),
    )

    set_style_visibility_to_hidden: Command[Union[Element, Collection]] = Command(
        'set element.style.visibility="hidden"',
        lambda entity: (
            entity.execute_script('element.style.visibility="hidden"')
            if not hasattr(entity, '__iter__')
            else [
                element.execute_script('element.style.visibility="hidden"')
                for element in entity
            ]
        ),
    )

    set_style_visibility_to_visible: Command[Union[Element, Collection]] = Command(
        'set element.style.visibility="visible"',
        lambda entity: (
            entity.execute_script('element.style.visibility="visible"')
            if not hasattr(entity, '__iter__')
            else [
                element.execute_script('element.style.visibility="visible"')
                for element in entity
            ]
        ),
    )
