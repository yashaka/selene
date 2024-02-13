# MIT License
#
# Copyright (c) 2024 Iakiv Kramarenko
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
from typing import Optional, List, Union, overload

from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import AnyDevice

from selene.core.entity import Element
from selene.core.configuration import Config
from selene.core.exceptions import _SeleneError
from selene.core.wait import Command, Query


@overload
def _ensure_located(element: Element | WebElement) -> WebElement: ...


@overload
def _ensure_located(element: Element | WebElement | None) -> WebElement | None: ...


def _ensure_located(element):
    return (
        element.get(Query('locate webelement', lambda it: it.locate()))
        if isinstance(element, Element)
        else element
    )


# TODO: refactor docstrings to the style used in Selene
# TODO: how will it work with Appium?
# TODO: should not we name it ActionsChain to differentiate from w3c actions?
# Selene does not like aliases because of PEP20, but here, in order to provide a better API,
# yet keeping compatibility with Selenium's ActionChains, we are using a lot of aliases
# TODO: but should we?
class _Actions:
    def __init__(
        self,
        config: Config,
        *,
        duration: int = 250,  # TODO: do we need this?
        #       should we have it in config instead?
        devices: Optional[List[AnyDevice]] = None,
    ):
        # TODO: below we pass driver as non lazy instance,
        #       that may lead to some issues in some multi-browser scenarios...
        #       should we bother about them?
        self._config = config
        # TODO: should we check here if driver is appium based
        #       and create proper instance correspondingly?
        self._chain = ActionChains(config.driver, duration, devices)

    def perform(self) -> None:
        def actions(chain: ActionChains):
            """
            if this fn will fail, the final error on wait will be something like:

            Timed out after 1s, while waiting for:
            <selenium.webdriver.common.action_chains.ActionChains object at 0x103115760>
            .{'actions': [[{'type': 'pointerMove', 'duration': 250, 'x': 0, 'y': 0,
             'origin': {'element-6066-11e4-a52e-4f735466cecf':
             '7F810F7CF30DD4907173DF4247841EB2_element_3'}},
             {'type': 'pointerDown', 'duration': 0, 'button': 0},
             {'type': 'pointerUp', 'duration': 0, 'button': 0}],
             [{'type': 'pause', 'duration': 0}, {'type': 'pause', 'duration': 0},
             {'type': 'pause', 'duration': 0}]]}

            TODO: can and should we improve it?
            """
            chain.perform()

        self._config.wait(self._chain).for_(Command(str(self.__encoded), actions))  # type: ignore

    @property
    def __encoded(self):
        return {
            'actions': list(
                filter(
                    None,
                    [
                        device.encode()['actions'] or None
                        for device in self._chain.w3c_actions.devices
                    ],
                )
            )
        }

    def click(self, on_element: Element | WebElement | None = None) -> _Actions:
        """Clicks an element.

        :Args:
         - on_element: The element to click.
           If None, clicks on current mouse position.
        """
        self._chain.click(_ensure_located(on_element))
        return self

    def click_and_hold(
        self, on_element: Element | WebElement | None = None
    ) -> _Actions:
        """Holds down the left mouse button on an element.

        :Args:
         - on_element: The element to mouse down.
           If None, clicks on current mouse position.
        """
        self._chain.click_and_hold(_ensure_located(on_element))
        return self

    def context_click(self, on_element: Element | WebElement | None = None) -> _Actions:
        """Performs a context-click (right click) on an element.

        :Args:
         - on_element: The element to context-click.
           If None, clicks on current mouse position.
        """
        self._chain.context_click(_ensure_located(on_element))
        return self

    def double_click(self, on_element: Element | WebElement | None = None) -> _Actions:
        """Double-clicks an element.

        :Args:
         - on_element: The element to double-click.
           If None, clicks on current mouse position.
        """
        self._chain.double_click(_ensure_located(on_element))
        return self

    def drag_and_drop(
        self, source: Element | WebElement, target: Element | WebElement
    ) -> _Actions:
        """Holds down the left mouse button on the source element, then moves
        to the target element and releases the mouse button.

        :Args:
         - source: The element to mouse down.
         - target: The element to mouse up.
        """
        self._chain.drag_and_drop(_ensure_located(source), _ensure_located(target))
        return self

    def drag_and_drop_by_offset(
        self, source: Element | WebElement, x: int, y: int
    ) -> _Actions:
        """Holds down the left mouse button on the source element, then moves
        to the target offset and releases the mouse button.

        :Args:
         - source: The element to mouse down.
         - xoffset: X offset to move to.
         - yoffset: Y offset to move to.
        """
        self._chain.drag_and_drop_by_offset(_ensure_located(source), x, y)
        return self

    def key_down(
        self, value: str, element: Element | WebElement | None = None
    ) -> _Actions:
        """Sends a key press only, without releasing it. Should only be used
        with modifier keys (Control, Alt and Shift).

        :Args:
         - value: The modifier key to send. Values are defined in `Keys` class.
         - element: The element to send keys.
           If None, sends a key to current focused element.

        Example, pressing ctrl+c::

            ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        """
        self._chain.key_down(value, _ensure_located(element))
        return self

    def key_up(
        self, value: str, element: Element | WebElement | None = None
    ) -> _Actions:
        """Releases a modifier key.

        :Args:
         - value: The modifier key to send. Values are defined in Keys class.
         - element: The element to send keys.
           If None, sends a key to current focused element.

        Example, pressing ctrl+c::

            ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        """
        self._chain.key_up(value, _ensure_located(element))
        return self

    def move_by_offset(self, x: int, y: int) -> _Actions:
        """Moving the mouse to an offset from current mouse position.

        :Args:
         - x: X offset to move to, as a positive or negative integer.
         - y: Y offset to move to, as a positive or negative integer.
        """
        self._chain.move_by_offset(x, y)
        return self

    def move_to_element(self, to_element: Element | WebElement) -> _Actions:
        """Moving the mouse to the middle of an element.

        :Args:
         - to_element: The WebElement to move to.
        """
        self._chain.move_to_element(_ensure_located(to_element))
        return self

    def move_to(self, element: Element | WebElement) -> _Actions:
        """Alias for move_to_element"""
        return self.move_to_element(element)

    def move_to_element_with_offset(
        self, to_element: Element | WebElement, xoffset: int, yoffset: int
    ) -> _Actions:
        """Move the mouse by an offset of the specified element. Offsets are
        relative to the in-view center point of the element.

        :Args:
         - to_element: The WebElement to move to.
         - xoffset: X offset to move to, as a positive or negative integer.
         - yoffset: Y offset to move to, as a positive or negative integer.
        """
        self._chain.move_to_element_with_offset(
            _ensure_located(to_element), xoffset, yoffset
        )
        return self

    def move_with_offset_to(
        self, element: Element | WebElement, x: int, y: int
    ) -> _Actions:
        """Alias for move_to_element_with_offset"""
        return self.move_to_element_with_offset(element, x, y)

    def pause(self, seconds: float | int) -> _Actions:
        """Pause all inputs for the specified duration in seconds."""
        self._chain.pause(seconds)
        return self

    def release(self, on_element: Element | WebElement | None = None) -> _Actions:
        """Releasing a held mouse button on an element.

        :Args:
         - on_element: The element to mouse up.
           If None, releases on current mouse position.
        """
        self._chain.release(_ensure_located(on_element))
        return self

    def send_keys(self, *keys_to_send: str) -> _Actions:
        """Sends keys to current focused element.

        :Args:
         - keys_to_send: The keys to send.  Modifier keys constants can be found in the
           'Keys' class.
        """
        self._chain.send_keys(*keys_to_send)
        return self

    def send_keys_to_element(
        self, element: Element | WebElement, *keys_to_send: str
    ) -> _Actions:
        """Sends keys to an element.

        :Args:
         - element: The element to send keys.
         - keys_to_send: The keys to send.  Modifier keys constants can be found in the
           'Keys' class.
        """
        self.click(element)
        self.send_keys(*keys_to_send)
        return self

    def send_keys_to(
        self, element: Element | WebElement, *keys_to_send: str
    ) -> _Actions:
        """Alias for send_keys_to_element"""
        return self.send_keys_to_element(element, *keys_to_send)

    def scroll_to_element(self, element: Element | WebElement) -> _Actions:
        """If the element is outside the viewport, scrolls the bottom of the
        element to the bottom of the viewport.

        :Args:
         - element: Which element to scroll into the viewport.
        """
        self._chain.scroll_to_element(_ensure_located(element))
        return self

    def scroll_to(self, element: Element | WebElement) -> _Actions:
        """Alias for scroll_to_element"""
        return self.scroll_to_element(element)

    def scroll_by_amount(self, delta_x: int, delta_y: int) -> _Actions:
        """Scrolls by provided amounts with the origin in the top left corner
        of the viewport.

        :Args:
         - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
         - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.
        """
        self._chain.scroll_by_amount(delta_x, delta_y)
        return self

    def scroll_by(self, delta_x: int, delta_y: int) -> _Actions:
        """Alias for scroll_by_amount"""
        return self.scroll_by_amount(delta_x, delta_y)

    def scroll_from_origin(
        self, scroll_origin: ScrollOrigin, delta_x: int, delta_y: int
    ) -> _Actions:
        """Scrolls by provided amount based on a provided origin. The scroll
        origin is either the center of an element or the upper left of the
        viewport plus any offsets. If the origin is an element, and the element
        is not in the viewport, the bottom of the element will first be
        scrolled to the bottom of the viewport.

        :Args:
         - origin: Where scroll originates (viewport or element center) plus provided offsets.
         - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
         - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.

         :Raises: If the origin with offset is outside the viewport.
          - MoveTargetOutOfBoundsException - If the origin with offset is outside the viewport.
        """
        self._chain.scroll_from_origin(scroll_origin, delta_x, delta_y)
        return self
