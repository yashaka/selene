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
import sys
from typing import Union, Optional, overload

from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.core.exceptions import _SeleneError
from selene.core.wait import Command
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput


# TODO: refactor to be of same style as __ClickWithOffset
#       in order to make autocomplete work properly
#       do it for save_screenshot and all other similar impls
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


def __select_all_actions(entity: Element | Browser):
    _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
    actions: ActionChains = ActionChains(entity.config.driver)

    actions.key_down(_COMMAND_KEY)

    if isinstance(entity, Element):
        actions.send_keys_to_element(entity.locate(), 'a')
    else:
        actions.send_keys('a')

    actions.key_up(_COMMAND_KEY)

    actions.perform()


select_all: Command[Element | Browser] = Command(
    'send «select all» keys shortcut as ctrl+a or cmd+a for mac',
    __select_all_actions,
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


# TODO: consider
#       .with(ensure_state_changed=True).perform(command.drag_and_drop_to(target))
#       over
#       .perform(command.drag_and_drop_to(target, assert_location_changed=True))
#       but how should we interpret `ensure_state_changed` for other commands?
#       – case by case? i.e. location_changed for drag_and_drop_to
#         and something different for other commands?
#       – or maybe actually check the overall state of the page,
#         i.e. something like page_source_changed or dom_changed?
#       what about:
#       perform(command.drag_and_drop_to(target).to_change_location())
#       over
#       .perform(command.drag_and_drop_to(target, assert_location_changed=True))


def drag_and_drop_to(
    target: Element, _assert_location_changed: bool = False
) -> Command[Element]:
    """
    Args:
        target: a destination element to drag and drop to
        _assert_location_changed: False by default, but if True,
            then will assert that element was dragged to the new location,
            hence forcing a command retry if command was under waiting.
            This option is marked as experimental (by leading underscore),
            it may be renamed or removed completely.
    """

    def func(source: Element):
        source_webelement = source.locate()
        source_location = (
            source_webelement.location if _assert_location_changed else None
        )

        ActionChains(source.config.driver).drag_and_drop(
            source_webelement,
            target.locate(),
        ).perform()

        if _assert_location_changed and source_location == source.locate().location:
            raise _SeleneError('Element was not dragged to the new place')

    return Command(f'drag and drop to: {target}', func)


# TODO: consider adding 0 as default for x and y
def drag_and_drop_by_offset(x: int, y: int) -> Command[Element]:
    def func(source: Element):
        ActionChains(source.config.driver).drag_and_drop_by_offset(
            source.locate(),
            x,
            y,
        ).perform()

    return Command(f'drag and drop by offset: x={x}, y={y}', func)


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

    # TODO: should we process collections too? i.e. click through all elements?
    class __ClickWithOffset(Command[Element]):
        def __init__(self):
            self._description = 'click'

        @overload
        def __call__(self, element: Element) -> None: ...

        @overload
        def __call__(self, *, xoffset=0, yoffset=0) -> Command[Element]: ...

        def __call__(self, element: Element | None = None, *, xoffset=0, yoffset=0):
            def func(element: Element):
                element.execute_script(
                    '''
                    const offsetX = arguments[0]
                    const offsetY = arguments[1]
                    const rect = element.getBoundingClientRect()

                    function mouseEvent() {
                      if (typeof (Event) === 'function') {
                        return new MouseEvent('click', {
                          view: window,
                          bubbles: true,
                          cancelable: true,
                          clientX: rect.left + rect.width / 2 + offsetX,
                          clientY: rect.top + rect.height / 2 + offsetY
                        })
                      }
                      else {
                        const event = document.createEvent('MouseEvent')
                        event.initEvent('click', true, true)
                        event.type = 'click'
                        event.view = window
                        event.clientX = rect.left + rect.width / 2 + offsetX
                        event.clientY = rect.top + rect.height / 2 + offsetY
                        return event
                      }
                    }
                    element.dispatchEvent(mouseEvent())
                    ''',
                    xoffset,
                    yoffset,
                )

            if element is not None:
                # somebody passed command as `.perform(command.js.click)`
                # not as `.perform(command.js.click())`
                func(element)
                return None

            return Command(
                (
                    self.__str__()
                    if (not xoffset and not yoffset)
                    else f'click(xoffset={xoffset},yoffset={yoffset})'
                ),
                func,
            )

    click = __ClickWithOffset()

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

    # TODO: add js.drag_and_drop_by_offset(x, y)

    @staticmethod
    def drag_and_drop_to(target: Element) -> Command[Element]:
        """
        Simulates drag and drop via JavaScript.

        May not work everywhere. Among known cases:
        * does not work on https://mui.com/material-ui/react-slider/#ContinuousSlider
          where the normal drag and drop works fine.
        """

        def func(source: Element):
            script = """
            (function() {
              function createEvent(typeOfEvent) {
                var event = document.createEvent('CustomEvent');
                event.initCustomEvent(typeOfEvent, true, true, null);
                event.dataTransfer = {
                  data: {},
                  setData: function(key, value) {
                    this.data[key] = value;
                  },
                  getData: function(key) {
                    return this.data[key];
                  }
                };
                return event;
              }

              function dispatchEvent(element, event, transferData) {
                if (transferData !== undefined) {
                  event.dataTransfer = transferData;
                }
                if (element.dispatchEvent) {
                  element.dispatchEvent(event);
                } else if (element.fireEvent) {
                  element.fireEvent("on" + event.type, event);
                }
              }

              function dragAndDrop(element, target) {
                var dragStartEvent = createEvent('dragstart');
                dispatchEvent(element, dragStartEvent);
                var dropEvent = createEvent('drop');
                dispatchEvent(target, dropEvent, dragStartEvent.dataTransfer);
                var dragEndEvent = createEvent('dragend');
                dispatchEvent(element, dragEndEvent, dropEvent.dataTransfer);
              }

              return dragAndDrop(arguments[0], arguments[1]);
            })(...arguments)
            """.strip()
            source.config.driver.execute_script(
                script,
                source.locate(),
                target.locate(),
            )

        return Command(f'drag and drop to: {target}', func)

    @staticmethod
    def drop_file(path: str) -> Command[Element]:
        """
        Simulates via JavaScript the “drag and drop” of file into self (this element).

        The command is useful in cases,
        when there is no actual hidden input of type file to `send_keys(path)` to.

        Args:
            path: an absolute path to the file
        """

        # TODO: should we move them to params?
        #       what do they actually do? something like this? –
        #           xoffset: x offset (from this element center) to drop file
        #           yoffset: y offset (from this element center) to drop file
        xoffset = 0
        yoffset = 0

        def func(source: Element):
            script = """
            var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;

            var input = document.createElement('INPUT');
            input.type = 'file';
            input.style.display = 'none';
            input.onchange = function () {
              var rect = target.getBoundingClientRect(),
                  x = rect.left + (offsetX || (rect.width >> 1)),
                  y = rect.top + (offsetY || (rect.height >> 1)),
                  dataTransfer = {
                    files: this.files,
                    types: [ 'Files' ],
                  };

              ['dragenter', 'dragover', 'drop'].forEach(function (name) {
                var evt = document.createEvent('MouseEvent');
                evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
                evt.dataTransfer = dataTransfer;
                target.dispatchEvent(evt);
              });

              setTimeout(function () { document.body.removeChild(input); }, 25);
            };
            document.body.appendChild(input);
            return input;
            """.strip()

            temp_input = source.config.driver.execute_script(
                script,
                source.locate(),
                xoffset,
                yoffset,
            )
            temp_input.send_keys(path)

            WebDriverWait(source.config.driver, 50).until(
                expected_conditions.staleness_of(temp_input)
            )

        return Command(f'drop file: {path}', func)
