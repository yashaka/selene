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

from abc import abstractproperty, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selene.abctypes.search_context import ISearchContext


class IWebElement(ISearchContext):

    @abstractproperty
    def __repr__(self): pass

    @abstractproperty
    def tag_name(self): pass

    @abstractproperty
    def text(self): pass

    @abstractmethod
    def click(self): pass

    @abstractmethod
    def submit(self): pass

    @abstractmethod
    def clear(self): pass

    @abstractmethod
    def get_attribute(self, name): pass

    @abstractmethod
    def is_selected(self): pass

    @abstractmethod
    def is_enabled(self): pass

    @abstractmethod
    def find_element_by_id(self, id_): pass

    @abstractmethod
    def find_elements_by_id(self, id_): pass

    @abstractmethod
    def find_element_by_name(self, name): pass

    @abstractmethod
    def find_elements_by_name(self, name): pass

    @abstractmethod
    def find_element_by_link_text(self, link_text): pass

    @abstractmethod
    def find_elements_by_link_text(self, link_text): pass

    @abstractmethod
    def find_element_by_partial_link_text(self, link_text): pass

    @abstractmethod
    def find_elements_by_partial_link_text(self, link_text): pass

    @abstractmethod
    def find_element_by_tag_name(self, name): pass

    @abstractmethod
    def find_elements_by_tag_name(self, name): pass

    @abstractmethod
    def find_element_by_xpath(self, xpath): pass

    @abstractmethod
    def find_elements_by_xpath(self, xpath): pass

    @abstractmethod
    def find_element_by_class_name(self, name): pass

    @abstractmethod
    def find_elements_by_class_name(self, name): pass

    @abstractmethod
    def find_element_by_css_selector(self, css_selector): pass

    @abstractmethod
    def find_elements_by_css_selector(self, css_selector): pass

    @abstractmethod
    def send_keys(self, *value): pass

    # RenderedWebElement Items
    @abstractmethod
    def is_displayed(self): pass

    @abstractproperty
    def location_once_scrolled_into_view(self): pass

    @abstractproperty
    def size(self): pass

    def value_of_css_property(self, property_name): pass

    @abstractproperty
    def location(self): pass

    @abstractproperty
    def rect(self): pass

    @abstractproperty
    def screenshot_as_base64(self): pass

    @abstractproperty
    def screenshot_as_png(self): pass

    @abstractmethod
    def screenshot(self, filename): pass

    @abstractproperty
    def parent(self): pass

    @abstractproperty
    def id(self): pass

    @abstractmethod
    def __eq__(self, element): pass

    @abstractmethod
    def __ne__(self, element): pass

    @abstractmethod
    def find_element(self, by=By.ID, value=None): pass

    @abstractmethod
    def find_elements(self, by=By.ID, value=None): pass

    @abstractmethod
    def __hash__(self): pass


IWebElement.register(WebElement)

