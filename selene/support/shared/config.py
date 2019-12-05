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


class SharedConfig(Config):

    _storage: List[Config] = []

    def set(self, config: Config):
        if not self._storage:
            self._storage.append(config)
        else:
            stored = self._storage.pop()
            self._storage.append(stored.with_(config))

    @property
    def _get(self) -> Config:  # todo: consider renaming to _stored or _shared
        return self._storage[0]

    @property
    def timeout(self) -> int:
        return self._get.timeout

    @timeout.setter
    def timeout(self, value: int):
        self.set(Config(timeout=value))

    @property
    def hold_browser_open(self) -> bool:
        return False  # todo: finish implementation

    @hold_browser_open.setter
    def hold_browser_open(self, value: bool):
        pass  # todo: finish implementation

    @property
    def driver(self) -> WebDriver:
        stored = self._get.driver
        is_alive = lambda: on_error_return_false(stored.title is not None)

        if stored and \
                stored.session_id and \
                is_alive() and \
                stored.name == self.browser_name:

            return stored

        stored.quit()  # todo: can this raise exception? that we need to supress...

        # todo: do we need here pass self.desired_capabilities too?
        new = {
            'chrome': lambda: Chrome(executable_path=ChromeDriverManager().install(),
                                     options=ChromeOptions()),
            'firefox': lambda: Firefox(executable_path=GeckoDriverManager().install())
        }.get(self.browser_name, 'chrome')()

        if not self.hold_browser_open:
            atexit.register(new.quit)

        self.set(Config(driver=new))

        return new

    @driver.setter
    def driver(self, value: WebDriver):
        is_another_driver = on_error_return_false(lambda: value.session_id != self.driver.session_id)

        if is_another_driver:
            self.driver.quit()  # todo: can quit raise exception? handle then...

        self.set(Config(driver=value))

        # noinspection PyDataclass
        self.browser_name = value.name

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
        return 'chrome'  # todo: finish implementation

    @browser_name.setter
    def browser_name(self, value: str):
        # todo: should we kill current driver if browser_name is changed?
        #       or should we open one more? so aftewards the user can switch...
        #       what about making such "mode" also configurable? ;)
        pass  # todo: finish implementation

    # todo: consider deprecating changing opts like timeout after driver was created
    #       make driver be recreated in such cases
    #       but again... what about making this configurable too? as a "mode"...

    # --- consider to depracate --- #

    @property
    def poll_during_waits(self) -> int:
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return 100

    @poll_during_waits.setter
    def poll_during_waits(self, value):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        pass

    @lru_cache()
    @property
    def counter(self):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return itertools.count(start=int(round(time.time() * 1000)))

    @counter.setter
    def counter(self, value):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        pass

    @property
    def reports_folder(self) -> str:
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        counter = itertools.count(start=int(round(time.time() * 1000)))
        return os.path.join(os.path.expanduser('~'), '.selene', 'screenshots', str(next(self.counter)))

    @reports_folder.setter
    def reports_folder(self, value):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        pass