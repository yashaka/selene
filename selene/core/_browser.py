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
from typing_extensions import Optional, Union

from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver

from selene.core._client import Client
from selene.core.configuration import Config


class Browser(Client):
    def __init__(self, config: Optional[Config] = None, **kwargs):
        warnings.warn(
            'selene.core.Browser is deprecated, use selene.core.Client instead',
            DeprecationWarning,
        )
        super().__init__(config=config, **kwargs)

    def __str__(self):
        return 'browser'

    # --- High Level Commands--- #

    def open(self, relative_or_absolute_url: Optional[str] = None) -> Browser:
        # TODO: should we keep it less pretty but more KISS? like:
        # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
        self.config._executor.get_url(relative_or_absolute_url)

        return self

    # TODO: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def quit(self) -> None:
        """
        Quits the driver.

        If the driver was not even set, will build it just to quit it:D.

        Will fail if the driver was already quit or crashed.
        """
        self.driver.quit()

    def close(self) -> Browser:
        self.driver.close()
        return self

    # --- Deprecated --- #

    def switch_to_next_tab(self) -> Browser:
        warnings.warn(
            'browser.switch_to_next_tab is deprecated',
            DeprecationWarning,
        )
        from selene.core import query

        self.driver.switch_to.window(query.next_tab(self))

        # TODO: should we use waiting version here (and in other similar cases)?
        # self.perform(Command(
        #     'open next tab',
        #     lambda browser: browser.driver.switch_to.window(query.next_tab(self))))

        return self

    def switch_to_previous_tab(self) -> Browser:
        warnings.warn(
            'browser.switch_to_previous_tab is deprecated',
            DeprecationWarning,
        )
        from selene.core import query

        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        warnings.warn(
            'browser.switch_to_tab is deprecated',
            DeprecationWarning,
        )
        if isinstance(index_or_name, int):
            index = index_or_name
            from selene.core import query

            self.driver.switch_to.window(query.tab(index)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    @property
    def switch_to(self) -> SwitchTo:
        warnings.warn(
            'browser.switch_to is considered to be deprecated',
            PendingDeprecationWarning,
        )
        return self.driver.switch_to
