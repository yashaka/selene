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
from typing import List

from selenium.webdriver import ChromeOptions, Chrome, Firefox
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selene.common.helpers import on_error_return_false
from selene.config import Config


# noinspection PyDataclass
class SharedConfig(Config):
    def __setattr__(self, attr, value):
        """unfreeze self"""
        object.__setattr__(self, attr, value)

    hold_browser_open: bool = False

    _driver: WebDriver = None
    _browser_name: str

    @property
    def driver(self) -> WebDriver:
        stored = self._driver
        is_alive = on_error_return_false(lambda: stored.title is not None)

        if stored and \
                stored.session_id and \
                is_alive and \
                stored.name == self.browser_name:

            return stored

        if stored:
            stored.quit()  # todo: can this raise exception? that we need to supress...

        # todo: do we need here pass self.desired_capabilities too?
        new = {
            'chrome': lambda: Chrome(executable_path=ChromeDriverManager().install(),
                                     options=ChromeOptions()),
            'firefox': lambda: Firefox(executable_path=GeckoDriverManager().install())
        }.get(self.browser_name)()

        if not self.hold_browser_open:
            atexit.register(new.quit)

        self._driver = new

        return new

    @driver.setter
    def driver(self, value: WebDriver):
        stored = self._driver
        is_another_driver = on_error_return_false(lambda: value.session_id != stored.session_id)

        if is_another_driver:
            stored.quit()  # todo: can quit raise exception? handle then...

        self._driver = value

        self.browser_name = value and value.name

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

    @property
    def browser_name(self) -> str:
        return self._browser_name or 'chrome'

    @browser_name.setter
    def browser_name(self, value: str):
        self._browser_name = value
        # todo: should we kill current driver if browser_name is changed?
        #       or should we open one more? so afterwards the user can switch...
        #       what about making such "mode" also configurable? ;)

    # todo: consider deprecating changing opts like timeout after driver was created
    #       make driver be recreated in such cases
    #       but again... what about making this configurable too? as a "mode"...

    # --- consider to depracate --- #

    _poll_during_waits: int

    @property
    def poll_during_waits(self) -> int:
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return self._poll_during_waits or 100

    @poll_during_waits.setter
    def poll_during_waits(self, value: int):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        self._poll_during_waits = value

    _counter = None

    @property
    @lru_cache()
    def counter(self):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return self._counter or itertools.count(start=int(round(time.time() * 1000)))

    @counter.setter
    def counter(self, value):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        self._counter = value

    _reports_folder: str

    @property
    def reports_folder(self) -> str:
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return self._reports_folder or os.path.join(
            os.path.expanduser('~'),
            '.selene',
            'screenshots',
            str(next(self.counter)))

    @reports_folder.setter
    def reports_folder(self, value):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        pass
