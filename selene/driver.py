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

"""The Selene's WebDriver Decorator implementation."""
from abc import ABCMeta, abstractproperty

from future.utils import with_metaclass
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from selene.abctypes.webdriver import IWebDriver
from selene.common.delegation import DelegatingMeta
from selene.common.none_object import NoneObject
from selene.elements import SeleneElement, SeleneCollection


class IWebDriverSource(with_metaclass(ABCMeta, object)):

    @abstractproperty
    def driver(self):
        # type: () -> WebDriver
        pass


# todo: consider implementing it like of DelegatingMeta
class ExplicitWebDriverSource(IWebDriverSource):
    @property
    def driver(self):
        return self._webdriver

    def __init__(self, webdriver):
        self._webdriver = webdriver


class SharedWebDriverSource(IWebDriverSource):

    @property
    def driver(self):
        return self._webdriver

    @driver.setter
    def driver(self, value):
        self._webdriver = value

    def __init__(self):
        self._webdriver = NoneObject("SharedWebDriverSource#_webdriver")  # type: IWebDriver


class SeleneDriver(with_metaclass(DelegatingMeta, IWebDriver)):

    @property
    def __delegate__(self):
        return self._webdriver

    @property
    def _webdriver(self):
        return self._source.driver

    # todo: consider the usage: `SeleneDriver(FirefoxDriver())` over `SeleneDriver.wrap(FirefoxDriver())`
    # todo: it may be possible if __init__ accepts webdriver_or_source and IWebDriverSource implements IWebDriver...
    @classmethod
    def wrap(cls, webdriver):
        # type: (WebDriver) -> SeleneDriver
        return SeleneDriver(ExplicitWebDriverSource(webdriver))

    # def __init__(self, webdriver):
    #     self._webdriver = webdriver

    def __init__(self, webdriver_source):
        # type: (IWebDriverSource) -> None
        self._source = webdriver_source

    def element(self, css_selector_or_by):
        return SeleneElement.by_css_or_by(css_selector_or_by, self)

    s = element
    find = element

    def all(self, css_selector_or_by):
        return SeleneCollection.by_css_or_by(css_selector_or_by, self)

    ss = all
    elements = all
    find_all = all

    # *** SearchContext methods ***
    def find_elements(self, by=By.ID, value=None):
        return self._webdriver.find_elements(by, value)
        # return self.find_all((by, value))

    def find_element(self, by=By.ID, value=None):
        return self._webdriver.find_element(by, value)
        # return self.find((by, value))


_shared_web_driver_source = SharedWebDriverSource()
_shared_driver = SeleneDriver(_shared_web_driver_source)