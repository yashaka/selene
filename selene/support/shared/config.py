# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
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
import itertools
import os
import time
import warnings
from functools import lru_cache
from typing import Optional, TypeVar, Generic, Callable

from selenium.webdriver import ChromeOptions, Chrome, Firefox, Remote
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selene.common.helpers import on_error_return_false
from selene.core.configuration import Config
from selene.core.exceptions import TimeoutException

T = TypeVar('T')


class Source(Generic[T]):
    def __init__(self, value: T = None):
        self._value = value

    def put(self, value: T):
        self._value = value

    @property
    def value(self) -> T:
        return self._value


# noinspection PyDataclass
class SharedConfig(Config):
    # todo: consider using SharedConfig object to be used as config only once... on init at first call to browser...
    #       i.e. do not allow config.* = ... after first call to e.g. browser.open, etc...
    #       since anyway this is a bad habit, better to use browser.with_(timeout=...), element.with_(...), etc.
    def __init__(self,
                 # Config
                 driver: Optional[WebDriver] = None,
                 timeout: int = 4,  # todo: consider removing defaults
                 base_url: str = '',
                 set_value_by_js: bool = False,
                 type_by_js: bool = False,
                 window_width: Optional[int] = None,
                 window_height: Optional[int] = None,
                 hook_wait_failure: Callable[[TimeoutException], Exception] = lambda e: e,
                 # SharedConfig
                 source: Source[WebDriver] = Source(),
                 browser_name: str = 'chrome',  # todo: rename to config.type? config.name? config.browser?
                 hold_browser_open: bool = False,
                 poll_during_waits: int = 100,
                 counter=None,  # default is set below
                 reports_folder: Optional[str] = None  # default is set below
                 ):
        self._source = source
        if driver:
            self._source.put(driver)
        self._browser_name = browser_name
        self._hold_browser_open = hold_browser_open
        self._poll_during_waits = poll_during_waits  # todo consider to deprecate
        self._counter = counter or itertools.count(start=int(round(time.time() * 1000)))  # todo: deprecate?
        self._reports_folder = reports_folder or os.path.join(os.path.expanduser('~'),
                                                              '.selene',
                                                              'screenshots',
                                                              str(next(self._counter)))
        super().__init__(driver=driver,
                         timeout=timeout,
                         base_url=base_url,
                         set_value_by_js=set_value_by_js,
                         type_by_js=type_by_js,
                         window_width=window_width,
                         window_height=window_height,
                         hook_wait_failure=hook_wait_failure)

    # --- Config.driver new "shared logic" --- #

    @property
    def driver(self) -> WebDriver:
        stored = self._source.value
        is_alive = on_error_return_false(lambda: stored.title is not None)

        if stored and \
                stored.session_id and \
                is_alive and \
                stored.name == self.browser_name:  # forces browser restart if config.browser_name was re-changed
            return stored

        if stored:
            stored.quit()  # todo: can this raise exception? that we need to supress...

        # todo: do we need here pass self.desired_capabilities too?
        new = {
            'chrome': lambda: Chrome(executable_path=ChromeDriverManager().install(),
                                     options=ChromeOptions()),
            'firefox': lambda: Firefox(executable_path=GeckoDriverManager().install())
        }.get(self.browser_name)()

        # todo: think on something like:
        #             'remote': lambda: Remote(**self.browser_name)
        #         }.get(self.browser_name if isinstance(self.browser_name, str) else 'remote')()

        if not self.hold_browser_open:
            atexit.register(new.quit)

        self._source.put(new)

        return new

    @driver.setter
    def driver(self, value: WebDriver):
        stored = self._source.value
        is_another_driver = on_error_return_false(lambda: value.session_id != stored.session_id)

        if is_another_driver:
            stored.quit()  # todo: can quit raise exception? handle then...

        self._source.put(value)

        self.browser_name = value and value.name  # overwrites default browser_name

        # todo: should we schedule driver closing on exit here too?

    # todo: consider accepting also hub url as "browser"
    #       because in case of "remote" mode, we will not need the common "name" like
    #       chrome or ff
    #       but we would pass the same name somewhere in caps... to choose correct "platform"
    #       so... then browser_name is kind of incorrect name becomes...
    #       why then not rename browser_name here to just browser...
    #       then... technically it might be possible to write something like:
    #           browser.config.browser = ... :)
    #              how can we make it impossible?
    #              or what else better name can we choose?

    # --- Config.* added setters --- #

    @Config.timeout.setter
    def timeout(self, value: int):
        self._timeout = value

    @Config.base_url.setter
    def base_url(self, value: str):
        self._base_url = value

    @Config.set_value_by_js.setter
    def set_value_by_js(self, value: bool):
        self._set_value_by_js = value

    @Config.type_by_js.setter
    def type_by_js(self, value: bool):
        self._type_by_js = value

    @Config.window_width.setter
    def window_width(self, value: Optional[int]):
        self._window_width = value

    @Config.window_height.setter
    def window_height(self, value: Optional[int]):
        self._window_height = value

    @Config.hook_wait_failure.setter
    def hook_wait_failure(self, value: Callable[[TimeoutException], Exception]):
        default = lambda e: e
        self._hook_wait_failure = value or default

    # --- SharedConfig.* new props --- #

    @property
    def hold_browser_open(self) -> bool:
        return self._hold_browser_open

    @hold_browser_open.setter
    def hold_browser_open(self, value: bool):
        self._hold_browser_open = value

    @property
    def browser_name(self) -> str:  # todo: consider renaming to... config.name? config.executor?
        return self._browser_name

    @browser_name.setter
    def browser_name(self, value: str):
        self._browser_name = value
        # todo: should we kill current driver if browser_name is changed? (now it's killed on next driver ask)
        #       or should we open one more? so afterwards the user can switch...
        #       what about making such "mode" also configurable? ;)

    # todo: consider deprecating changing opts like timeout after driver was created
    #       make driver be recreated in such cases
    #       but again... what about making this configurable too? as a "mode"...

    # --- consider to depracate --- #

    @property
    def poll_during_waits(self) -> int:
        warnings.warn('browser.poll_during_waits might be deprecated', PendingDeprecationWarning)
        return self._poll_during_waits or 100

    @poll_during_waits.setter
    def poll_during_waits(self, value: int):
        warnings.warn('browser.poll_during_waits= might be deprecated', PendingDeprecationWarning)
        self._poll_during_waits = value

    @property
    @lru_cache()
    def counter(self):
        warnings.warn('browser.counter might be deprecated', PendingDeprecationWarning)
        return self._counter

    @counter.setter
    def counter(self, value):
        warnings.warn('browser.counter= might be deprecated', PendingDeprecationWarning)
        self._counter = value

    @property
    def reports_folder(self) -> str:
        warnings.warn('browser.reports_folder might be deprecated', PendingDeprecationWarning)
        return self._reports_folder

    @reports_folder.setter
    def reports_folder(self, value):
        warnings.warn('browser.reports_folder= might be deprecated', PendingDeprecationWarning)
        self._reports_folder = value
