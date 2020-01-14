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

from _ast import Dict, List
from _ctypes import Union
from abc import abstractmethod, abstractproperty
from contextlib import contextmanager

from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.html5.application_cache import ApplicationCache
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selene.abctypes.search_context import ISearchContext


class IWebDriver(ISearchContext):
    @abstractmethod
    def __repr__(self):
        # type: () -> str
        pass

    @contextmanager
    @abstractmethod
    def file_detector_context(self, file_detector_class, *args, **kwargs):
        pass

    @abstractproperty
    def mobile(self):
        # type: () -> Mobile
        pass

    @abstractproperty
    def w3c(self):
        # type: () -> bool
        pass

    @abstractproperty
    def name(self):
        # type: () -> str
        pass

    @abstractmethod
    def w3c(self):
        pass

    @abstractmethod
    def start_client(self):
        # type: () -> None
        pass

    @abstractmethod
    def stop_client(self):
        # type: () -> None
        pass

    @abstractmethod
    def start_session(self, desired_capabilities, browser_profile=None):
        # type: () -> None
        pass

    @abstractmethod
    def _wrap_value(self, value):
        pass

    @abstractmethod
    def create_web_element(self, element_id):
        # type: (object) -> WebElement
        # todo: object? str?
        pass

    @abstractmethod
    def _unwrap_value(self, value):
        pass

    @abstractmethod
    def execute(self, driver_command, params=None):
        # type: (str, Dict) -> Dict
        pass

    @abstractmethod
    def get(self, url):
        # type: (str) -> Dict
        pass

    @abstractproperty
    def title(self):
        # type: () -> str
        pass

    @abstractmethod
    def find_element_by_id(self, id_):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_id(self, id_):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_xpath(self, xpath):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_xpath(self, xpath):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_link_text(self, link_text):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_link_text(self, text):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_partial_link_text(self, link_text):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_partial_link_text(self, link_text):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_name(self, name):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_name(self, name):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_tag_name(self, name):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_tag_name(self, name):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_class_name(self, name):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_class_name(self, name):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def find_element_by_css_selector(self, css_selector):
        # type: (str) -> WebElement
        pass

    @abstractmethod
    def find_elements_by_css_selector(self, css_selector):
        # type: (str) -> List[WebElement]
        pass

    @abstractmethod
    def execute_script(self, script, *args):
        # type: (str, *object) -> str
        pass

    @abstractmethod
    def execute_async_script(self, script, *args):
        # type: (str, *object) -> str
        pass

    @abstractproperty
    def current_url(self):
        # type: () -> str
        pass

    @abstractproperty
    def page_source(self):
        # type: () -> str
        pass

    @abstractmethod
    def close(self):
        # type: () -> None
        pass

    @abstractmethod
    def quit(self):
        # type: () -> None
        pass

    @abstractproperty
    def current_window_handle(self):
        # type: () -> str
        pass

    @abstractproperty
    def window_handles(self):
        # todo: add type annotation
        pass

    @abstractmethod
    def maximize_window(self):
        # type: () -> None
        pass

    @abstractproperty
    def switch_to(self):
        # type: () -> SwitchTo
        pass

    # *** Target Locators ***

    @abstractmethod
    def switch_to_active_element(self):
        # type: () -> object
        # todo: object? WebElement?
        pass

    @abstractmethod
    def switch_to_window(self, window_name):
        # type: () -> None
        pass

    @abstractmethod
    def switch_to_frame(self, frame_reference):
        # type: () -> None
        pass

    @abstractmethod
    def switch_to_default_content(self):
        # type: () -> None
        pass

    @abstractmethod
    def switch_to_alert(self):
        # type: () -> Alert
        pass

    # *** Navigation ***

    @abstractmethod
    def back(self):
        # type: () -> None
        pass

    @abstractmethod
    def forward(self):
        # type: () -> None
        pass

    @abstractmethod
    def refresh(self):
        # type: () -> None
        pass

    # *** Options ***

    @abstractmethod
    def get_cookies(self):
        # type: () -> Union[str, unicode]
        # todo: Union? Dict?
        pass

    @abstractmethod
    def get_cookie(self, name):
        # todo: type?
        pass

    @abstractmethod
    def delete_cookie(self, name):
        # type: () -> None
        pass

    @abstractmethod
    def delete_all_cookies(self):
        # type: () -> None
        pass

    @abstractmethod
    def add_cookie(self, cookie_dict):
        # type: () -> None
        pass

    # *** Timeouts ***

    @abstractmethod
    def implicitly_wait(self, time_to_wait):
        # type: (int) -> None
        pass

    @abstractmethod
    def set_script_timeout(self, time_to_wait):
        # type: (int) -> None
        pass

    @abstractmethod
    def set_page_load_timeout(self, time_to_wait):
        # type: (int) -> None
        pass

    # @abstractmethod
    # def find_element(self, by=By.ID, value=None):
    #     pass
    #
    # @abstractmethod
    # def find_elements(self, by=By.ID, value=None):
    #     pass

    @abstractproperty
    def desired_capabilities(self):
        # type: () -> Dict
        pass

    @abstractmethod
    def get_screenshot_as_file(self, filename):
        # type: (str) -> bool
        pass

    save_screenshot = get_screenshot_as_file

    @abstractmethod
    def get_screenshot_as_png(self):
        # type: () -> object
        # todo: type?
        pass

    @abstractmethod
    def get_screenshot_as_base64(self):
        # todo: type?
        pass

    @abstractmethod
    def set_window_size(self, width, height, windowHandle='current'):
        # type: (object, object, str) -> None
        pass

    @abstractmethod
    def get_window_size(self, windowHandle='current'):
        # type: (str) -> Dict
        pass

    @abstractmethod
    def set_window_position(self, x, y, windowHandle='current'):
        # type: (object, object, str) -> None
        pass

    @abstractmethod
    def get_window_position(self, windowHandle='current'):
        # type: (str) -> Dict
        pass

    @abstractproperty
    def file_detector(self):
        # type: () -> FileDetector
        pass

    @file_detector.setter
    @abstractmethod
    def file_detector(self, detector):
        # type: (FileDetector) -> None
        pass

    @abstractproperty
    def orientation(self):
        # todo: type?
        pass

    @orientation.setter
    @abstractmethod
    def orientation(self, value):
        # todo: type?
        pass

    @abstractproperty
    def application_cache(self):
        # type: () -> ApplicationCache
        pass

    @abstractproperty
    def log_types(self):
        # todo: type?
        pass

    @abstractmethod
    def get_log(self, log_type):
        # todo: type?
        pass

IWebDriver.register(WebDriver)
