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
"""
# Module overview

This module contains a set of advanced commands that can be used in addition
to the standard Selene commands. Given a Selene entity,
i.e. an object of type `Browser | Collection | Element`,
a standard Selene command is any method of the entity (among `entity.*` methods)
that performs an action on entity and returns the entity itself.
Then an advanced command is the one defined outside the entity class
and given named as `advanced_command` then can be executed on entity
via `entity.perform(advanced_command)`.

The idiomatic way to use advanced commands is to import the whole module:

```python
from selene import browser, command  # ❗️over from ...command import drag_and_drop_to

slider = browser.element('#ContinuousSlider+*')
slider_thumb = slider.element('.MuiSlider-thumb')
slider_volume_up = slider.element('[data-testid=VolumeUpIcon]')
slider_thumb_input = slider_thumb.element('input')

# GIVEN
browser.open('https://mui.com/material-ui/react-slider/#ContinuousSlider')

# WHEN
slider_thumb.perform(command.drag_and_drop_to(slider_volume_up))  # ⬅️ used via module

# THEN
slider_thumb_input.should(have.value('100'))
```

Thus you don't need to remember all available advanced commands,
you just import the module and select the one you need
from the list of suggestions among `command.*`.

# Why do we need a separate module for advanced commands?

advanced commands are defined outside of the entity class,
because they can hardly be implemented in most versatile way.
Some of them will work only in a specific web application context,
others will not work on a mobile device, etc.
Thus, by separating advanced commands from the standard ones,
we emphasize for the end user of Selene – the importance
of more conscious use of them.

!!! tip

    Yet you can always [extend Selene][how-to-extend-selene] entities
    with your own commands built in.

The list of advanced commands in this module is far from exhaustive,
and there is no goal to make it complete, because in many cases, the end user
will need his own list of custom commands specific to his application context.
But this list can be a good starting point for such custom commands.
Taking the latter into account we try to keep implementation of the commands
in this module – as simple as possible,
so that the end user can easily understand them
and use as examples to implement own custom commands.
That's why we avoid following DRY principle here,
and prefer pure selenium code
over reusing already implemented in Selene helpers.

# How to implement custom advanced commands?

In case you need your own set of custom commands for Selene,
we recommend the following pattern.
Given your project named as `my_tests_project`, in the root package
of your project, at proper place, create your own module `command.py`:

## Example: custom command without parameters

```python
# Full path can be: my_tests_project/extensions/selene/command.py

# Next import is an important part of the “pattern”
# It will allow to reuse all existing advanced Selene commands.
# Thus you are extending Selene commands, without doubling efforts in usage.
from selene.core.command import *

# Some imports below are not mandatory,
# because are already among `*` from the import above,
# but we still mention them below for self-documentation purposes.

# To customize commands representation in logs
# by wrapping them into Command object:
from selene.core.wait import Command

# For type hints:
from selene import Element, Browser, Collection

# Usually you build your custom commands on top of pure Selenium's ActionChains
from selenium.webdriver import ActionChains, Keys

# To define current platform:
import sys


# Here goes an actual custom command implementation...
# We prefix command with underscore by marking it as "not for actual use",
# because we want to build another version of this command,
# with a more representative name (more on that later...)
def _select_all_and_copy(
        # by providing two entity types in type hints...
        entity: Element | Browser,
        # – we self-document the fact
        #   that command will work on both Element and Browser
    ):
    '''Selects all text under the focus if called on browser
    or all text in the element if called on element,
    then copies it to the clipboard.
    For both selecting and copying uses OS-based keys combination.

    If had been failed, then is logged to console with it's function name,
    i.e. '_select_all_and_copy', for example:

        Timed out after 4s, while waiting for:
        browser.element(('css selector', '#new-task'))._select_all_and_copy

    '''

    _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

    actions = ActionChains(entity.config.driver)

    # select all
    actions.key_down(_COMMAND_KEY)
    if isinstance(entity, Element):
        actions.send_keys_to_element(entity.locate(), 'a')
    else:
        actions.send_keys('a')
    actions.key_up(_COMMAND_KEY)

    # copy
    actions.key_down(_COMMAND_KEY)
    if isinstance(entity, Element):
        actions.send_keys_to_element(entity.locate(), 'c')
    else:
        actions.send_keys('c')
    actions.key_up(_COMMAND_KEY)

    actions.perform()


# Any function on entity that returns void – is already a valid command,
# and can be used as follows:
# >>> from my_tests_project.extensions.selene import command
# >>> browser.element('#new-task').perform(command._select_all_and_copy)
# Then if failed, it will be logged as:
#     Timed out after 4s, while waiting for:
#     browser.element(('css selector', '#new-task'))._select_all_and_copy
# If we want a more representative name in logs,
# we can wrap such command-as-function into Command object:

select_all_and_copy: Command[Element | Browser] = Command(
    'send «select all» and «copy» keys shortcut',
    _select_all_and_copy,
)

# Then we can use it as follows:
# >>> from my_tests_project.extensions.selene import command
# >>> browser.element('#new-task').perform(command.select_all_and_copy)
# And if failed, it will be logged as:
#     Timed out after 4s, while waiting for:
#     browser.element(('css selector', '#new-task')).send «select all»
#      and «copy» keys shortcut
```

## Tuning the usage of custom commands module

Note, that since we used `from selene.core.command import *`
when defining our custom commands module, we don't need in usage to import both –
original selene module and our custom new one:

```python
from selene import browser, command as original
from my_project_root.extensions.selene import command

browser.open('https://todomvc-emberjs-app.autotest.how/')
browser.element('#new-todo').type('foo').perform(command.select_all_and_copy)
browser.element('#new-todo').perform(original.js.set_value('reset'))
```

It's completely enough here and everywhere in your project
to use only your own module import:

```python
from selene import browser,
from my_project_root.extensions.selene import command

browser.open('https://todomvc-emberjs-app.autotest.how/')
browser.element('#new-todo').type('foo').perform(command.select_all_and_copy)
browser.element('#new-todo').perform(command.js.set_value('reset'))
```

When applying the “Quick fix” functionality of your IDE of choice
to the `command` term in the code yet without import:

```python
from selene import browser,

browser.open('https://todomvc-emberjs-app.autotest.how/')
browser.element('#new-todo').type('foo').perform(command.select_all_and_copy)
browser.element('#new-todo').perform(command.js.set_value('reset'))
```

You will get both suggestions, and, maybe with not quite handy sorting:

```text
                 Import from...
command from selene
command from my_project_root.extensions.selene
```

If you find uncomfortable to allways waste
an additional time to “select the second one from the list”,
you can name your module as `action.py`,
then you'll probably get the top-sorted suggestion
of `action from my_project_root.extensions.selene` import
for the code like:

```python
from selene import browser,

browser.open('https://todomvc-emberjs-app.autotest.how/')
browser.element('#new-todo').type('foo').perform(action.select_all_and_copy)
browser.element('#new-todo').perform(action.js.set_value('reset'))
```

Yet keeping the already defined naming in Selene – the “command” one –
has its own benefits for the purpose of consistency
and less amount of terminology. But for you to decide.
You can find your own name that better suits your project context.

## Example: custom command with parameter

Sometimes your command needs an additional parameter.
Then you have to implement the so called “command builder”, for example:

```python
def press_sequentially(keys: str):
    def action(element: Element):
        actions = ActionChains(element.config.driver)

        for key in keys:
            actions.send_keys_to_element(element.locate(), Keys.END + key)

        actions.perform()

    return Command(f'press sequentially: {keys}', action)

```

Here the actual command is the `action` function
defined inside the definition of the `press_sequentially` command builder,
and returned from it wrapped in a more “descriptive” `Command` object.

For more examples of how to build your own custom commands
see the actual implementation of Selene's advanced commands in this module.

# The actual list of commands ↙️
"""
from __future__ import annotations
import sys
from typing import Union, Optional, overload

from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selene.core import entity
from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.core.exceptions import _SeleneError
from selene.common._typing_functions import Command
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

    if entity._wraps_driver(path):
        # somebody passed command as `.perform(command.save_screenshot)`
        # not as `.perform(command.save_screenshot())`
        driver_wrapper = path
        command.__call__(driver_wrapper)

    return command


def save_page_source(path: Optional[str] = None) -> Command[Browser]:
    command: Command[Browser] = Command(
        'save page source',
        lambda browser: browser.config._save_page_source_strategy(browser.config, path),
    )

    if entity._wraps_driver(path):
        # somebody passed command as `.perform(command.save_screenshot)`
        # not as `.perform(command.save_screenshot())`
        driver_wrapper = path
        command.__call__(driver_wrapper)

    return command


def __select_all_actions(some_entity: Element | Browser):
    _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
    actions: ActionChains = ActionChains(some_entity.config.driver)

    actions.key_down(_COMMAND_KEY)

    if entity._is_element(some_entity):
        actions.send_keys_to_element(some_entity.locate(), 'a')  # type: ignore
    else:
        actions.send_keys('a')

    actions.key_up(_COMMAND_KEY)

    actions.perform()


select_all: Command[Element | Browser] = Command(
    'send «select all» keys shortcut as ctrl+a or cmd+a for mac',
    __select_all_actions,
)


def copy_and_paste(text: str):
    """Copies text to clipboard programmatically and pastes it to the element
    by pressing OS-based keys combination.

    Requires pyperclip package to be installed.

    Does not support mobile context. Not tested with desktop apps.
    """

    def action(some_entity: Element | Browser):
        try:
            import pyperclip  # type: ignore
        except ImportError as error:
            raise ImportError(
                'pyperclip package is not installed, '
                'run `pip install pyperclip`,'
                'or add and install dependency '
                'with your favorite dependency manager like poetry: '
                '`poetry add pyperclip`'
            ) from error

        _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

        pyperclip.copy(text)

        actions = ActionChains(some_entity.config.driver)
        actions.key_down(_COMMAND_KEY)
        if entity._is_element(some_entity):
            actions.send_keys_to_element(some_entity.locate(), 'v')  # type: ignore
        else:
            actions.send_keys('v')
        actions.key_up(_COMMAND_KEY)
        actions.perform()

    return Command(f'copy and paste: {text}»', action)


def __copy(some_entity: Element | Browser):
    _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

    actions = ActionChains(some_entity.config.driver)
    actions.key_down(_COMMAND_KEY)
    if entity._is_element(some_entity):
        actions.send_keys_to_element(some_entity.locate(), 'c')  # type: ignore
    else:
        actions.send_keys('c')
    actions.key_up(_COMMAND_KEY)
    actions.perform()


# TODO: define name dynamically based on platform
copy: Command[Element | Browser] = Command(
    'send «copy» keys shortcut as ctrl+c for win/linux or cmd+c for mac',
    __copy,
)


def __paste(some_entity: Element | Browser):
    _COMMAND_KEY = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

    actions = ActionChains(some_entity.config.driver)
    actions.key_down(_COMMAND_KEY)
    if entity._is_element(some_entity):
        actions.send_keys_to_element(some_entity.locate(), 'v')  # type: ignore
    else:
        actions.send_keys('v')
    actions.key_up(_COMMAND_KEY)
    actions.perform()


# TODO: define name dynamically based on platform
paste: Command[Element | Browser] = Command(
    'send «paste» keys shortcut as ctrl+v for win/linux or cmd+v for mac',
    __paste,
)


# TODO: can we make it work for both mobile and web?
#       should we selectively choose proper interaction.POINTER_TOUCH below?
# TODO: consider renaming to touch_long_press
#       or consider checking the mobile context and change impl dynamically
#       see also: https://ux.stackexchange.com/questions/98410/terminology-long-press-or-touch-hold
def long_press(duration=1.0):
    """A mobile “long press” command, also known as “touch and hold”.

    Args:
        duration (float): duration of the hold between press and release in seconds

    !!! warning

        Designed for the mobile context only. Not tested for web.
    """

    def action(entity: Element):
        located_element = entity.locate()
        driver = entity.config.driver
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

    command = Command(f'long press with duration={duration}', action)

    if entity._is_element(duration):
        # somebody passed command as `.perform(command.long_press)`
        # not as `.perform(command.long_press())`
        # TODO: refactor to really allow such use case without conflicts on types
        element = duration
        command.__call__(element)

    return command


# TODO: deprecate
_long_press = long_press
"""An outdated alias to the `long_press` command.
"""


def press_sequentially(text: str):
    """Presses each key (letter) in text sequentially to the element.

    The pure webelement.send_keys already does it, but this command simulates
    more slow human-like typing by applying send_keys to each key
    of the text passed with additional END key press before each next key
    to ensure that each next key is typed at the end of the text.

    Such weird simulation might help with some rare cases of "slow" text fields,
    that extensively loads some other content on each key press,
    for example the content of auto-suggestions, etc.
    """

    def action(element: Element):
        actions = ActionChains(element.config.driver)

        for key in text:
            actions.send_keys_to_element(element.locate(), Keys.END + key)

        actions.perform()

    return Command(f'press sequentially: {text}', action)


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
    """A container for JavaScript-based commands.

    Examples:
        >>> from selene import browser, command
        >>> browser.element('#new-todo').perform(command.js.set_value('abc'))

    !!! danger
        Don't use them in mobile context! JavaScript doesn't work their.
    """

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
            self._name = 'click'

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

        !!! warning

            May not work everywhere. Among known cases:
            does not work on [Material UI React Continuous Slider](https://mui.com/material-ui/react-slider/#ContinuousSlider)
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
