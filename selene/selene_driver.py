"""The Selene's WebDriver Decorator implementation."""
from _ast import List, Tuple, Dict
from _ctypes import Union
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Sequence
from contextlib import contextmanager

from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.html5.application_cache import ApplicationCache
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.none_object import NoneObject
from selene.conditions import Condition
from selene.support.conditions import be
from selene.support.conditions import have
from core.delegation import DelegatingMeta
from selene import config
from selene.wait import wait_for, wait_for_not

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


class ISearchContext(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def find_element(self, by=By.ID, value=None):
        # type: (By, str) -> WebElement
        raise NotImplementedError

    @abstractmethod
    def find_elements(self, by=By.ID, value=None):
        # type: (By, str) -> List[WebElement]
        raise NotImplementedError


ISearchContext.register(WebDriver)
ISearchContext.register(WebElement)


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
    def name(self):
        # type: () -> str
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


class IWebElement(ISearchContext):
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


class ISeleneWebElementLocator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def find(self):
        # type: () -> WebElement
        pass

    @abstractproperty
    def description(self):
        # type: () -> str
        pass

    def __str__(self):
        return self.description


class ISeleneListWebElementLocator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def find(self):
        # type: () -> List[WebElement]
        raise NotImplementedError

    @abstractproperty
    def description(self):
        # type: () -> str
        raise NotImplementedError

    def __str__(self):
        return self.description


# todo: consider renaming/refactoring to WebDriverWebElementLocator...
class SearchContextWebElementLocator(ISeleneWebElementLocator):
    def __init__(self, by, search_context):
        # type: (Tuple[By, str], ISearchContext) -> None
        self._by = by
        self._search_context = search_context

    @property
    def description(self):
        return "By.Selene: (%s).find(%s)" % (self._search_context, self._by)

    def find(self):
        return self._search_context.find_element(*self._by)


class InnerWebElementLocator(ISeleneWebElementLocator):
    def __init__(self, by, element):
        # type: (Tuple[By, str], SeleneElement) -> None
        self._by = by
        self._element = element

    @property
    def description(self):
        return "By.Selene: (%s).find(%s)" % (self._element, self._by)

    def find(self):
        # return self._element.should(be.in_dom).find_element(*self._by)
        return self._element.should(be.visible).find_element(*self._by)
        # todo: should(be.in_dom) or be.visible?


class CachingWebElementLocator(ISeleneWebElementLocator):
    @property
    def description(self):
        return "Caching %" + (self._element,)

    @lru_cache()
    def find(self):
        return self._element()

    def __init__(self, element):
        self._element = element


# todo: PyCharm generates abstract methods impl before __init__ method.
# todo: Should we use this order convention? like below...
class IndexedWebElementLocator(ISeleneWebElementLocator):
    def find(self):
        delegate = self._collection.should(have.size_at_least(self._index + 1))
        return delegate()[self._index]

    @property
    def description(self):
        return "By.Selene: (%s)[%s]" % (self._collection, self._index)

    def __init__(self, index, collection):
        # type: (int, SeleneCollection) -> None
        self._index = index
        self._collection = collection


class SearchContextListWebElementLocator(ISeleneListWebElementLocator):
    def __init__(self, by, search_context):
        # type: (Tuple[By, str], ISearchContext) -> None
        self._by = by
        self._search_context = search_context

    @property
    def description(self):
        return "By.Selene: (%s).find_all(%s)" % (self._search_context, self._by)

    def find(self):
        return self._search_context.find_elements(*self._by)


class InnerListWebElementLocator(ISeleneListWebElementLocator):
    def __init__(self, by, element):
        # type: (Tuple[By, str], SeleneElement) -> None
        self._by = by
        self._element = element

    @property
    def description(self):
        return "By.Selene: (%s).find_all(%s)" % (self._element, self._by)

    def find(self):
        # return self._element.should(be.in_dom).find_elements(*self._by)
        return self._element.should(be.visible).find_elements(*self._by)
        # todo: should(be.in_dom) or be.visible?


class FilteredListWebElementLocator(ISeleneListWebElementLocator):
    def find(self):
        webelements = self._collection()
        filtered = [webelement
                    for webelement in webelements
                    if self._condition.matches_webelement(webelement)]
        return filtered

    @property
    def description(self):
        return "By.Selene: (%s).filter_by(%s)" % (self._collection, self._condition.description())

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


class SlicedListWebElementLocator(ISeleneListWebElementLocator):
    def find(self):
        self._collection.should(have.size_at_least(self._slice.stop))
        webelements = self._collection()
        return webelements[self._slice.start:self._slice.stop:self._slice.step]

    @property
    def description(self):
        return "By.Selene: (%s)[%s:%s:%s]" % (self._collection, self._slice.start, self._slice.stop, self._slice.step)

    def __init__(self, slc,  collection):
        # type: (slice, SeleneCollection) -> None
        self._slice = slc
        self._collection = collection


class FoundByConditionWebElementLocator(ISeleneWebElementLocator):
    def find(self):
        for webelement in self._collection():
            if self._condition.matches_webelement(webelement):
                return webelement
        raise NoSuchElementException('Element was not found by: %s' % (self.description,))

    @property
    def description(self):
        return "By.Selene: (%s).find_by(%s)" % (self._collection, self._condition.description())

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


def css_or_by_to_by(css_selector_or_by):
    # todo: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
    if isinstance(css_selector_or_by, tuple):
        return css_selector_or_by
    if isinstance(css_selector_or_by, str):
        return (By.CSS_SELECTOR, css_selector_or_by)
    raise TypeError('css_selector_or_by should be str with CSS selector or Tuple[by:str, value:str]')


class SeleneElement(IWebElement):
    __metaclass__ = DelegatingMeta

    @property
    def __delegate__(self):
        return self._locator.find()

    # todo: is this alias needed?
    _get_actual_webelement = __delegate__

    # todo: consider removing this method once conditions will be refactored
    # todo: (currently Condition impl depends on this method)
    def __call__(self):
        return self.__delegate__

    # todo: or... maybe better will be remove __delegate__, and just use __call_ instead... ?

    @classmethod
    def by(cls, by, webdriver, context=None):
        # type: (Tuple[str, str], IWebDriver, ISearchContext) -> SeleneElement
        if not context:
            context = webdriver

        return SeleneElement(SearchContextWebElementLocator(by, context), webdriver)

    @classmethod
    def by_css(cls, css_selector, webdriver, context=None):
        # type: (str, IWebDriver, ISearchContext) -> SeleneElement
        if not context:
            context = webdriver

        return SeleneElement.by((By.CSS_SELECTOR, css_selector), webdriver, context)

    @classmethod
    def by_css_or_by(cls, css_selector_or_by, webdriver, context=None):
        if not context:
            context = webdriver

        return SeleneElement.by(
            css_or_by_to_by(css_selector_or_by),
            webdriver,
            context)

    # todo: consider renaming webdriver to driver, because actually SeleneDriver also can be put here...
    def __init__(self, selene_locator, webdriver):
        # type: (ISeleneWebElementLocator, WebDriver) -> None
        self._locator = selene_locator
        self._webdriver = webdriver
        self._actions_chains = ActionChains(webdriver)

    def __str__(self):
        return self._locator.description

    def element(self, css_selector_or_by):
        return SeleneElement(
            InnerWebElementLocator(css_or_by_to_by(css_selector_or_by), self),
            self._webdriver)

    s = element
    find = element
    # todo: consider making find a separate not-lazy method (not alias)
    # to be used in such example: s("#element").hover().find(".inner").click()
    #                       over: s("#element").hover().element(".inner").click()
    # todo: should then all action-commands return cached elements by default?

    # todo: this is an object, it does not find. should we switch from method to "as a property" implementation?
    def caching(self):
        return SeleneElement(CachingWebElementLocator(self), self._webdriver)

    # todo: cached or cache?
    def cached(self):
        caching = self.caching()
        return caching.should(be.in_dom)

    def all(self, css_selector_or_by):
        # return SeleneCollection.by_css_or_by(css_selector_or_by, self._webdriver, context=self)
        return SeleneCollection(
            InnerListWebElementLocator(css_or_by_to_by(css_selector_or_by), self),
            self._webdriver)

    ss = all
    elements = all
    find_all = all

    def should(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        # todo: implement proper cashing
        # self._found = wait_for(self, condition, condition, timeout)
        wait_for(self, condition, condition, timeout)
        return self

    # todo: consider removing some aliases
    insist = should
    assure = should
    should_be = should
    should_have = should

    def should_not(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        # todo: implement proper cashing
        wait_for_not(self, condition, condition, timeout)
        return self

    # todo: consider removing some aliases
    insist_not = should_not
    assure_not = should_not
    should_not_be = should_not
    should_not_have = should_not

    def double_click(self):
        self._execute(
            lambda: self._actions_chains.double_click(self.__delegate__).perform(),
            condition=be.visible)
        return self

    def set(self, new_text_value):

        def clear_and_send_keys():
            self.__delegate__.clear()
            self.__delegate__.send_keys(new_text_value)

        self._execute(
            clear_and_send_keys,
            condition=be.visible)

        return self

    set_value = set

    def press_enter(self):
        return self.send_keys(Keys.ENTER)

    def press_escape(self):
        return self.send_keys(Keys.ESCAPE)

    def press_tab(self):
        return self.send_keys(Keys.TAB)

    def hover(self):
        self._execute(
            lambda: self._actions_chains.move_to_element(self.__delegate__).perform(),
            condition=be.visible)
        return self

    # *** ISearchContext methods ***

    def find_elements(self, by=By.ID, value=None):
        return self.__delegate__.find_elements(by, value)

    def find_element(self, by=By.ID, value=None):
        return self.__delegate__.find_element(by, value)

    # *** IWebElement methods ***

    @property
    def tag_name(self):
        return self._execute(
            lambda: self.__delegate__.tag_name,
            condition=be.in_dom)

    @property
    def text(self):
        return self._execute(
            lambda: self.__delegate__.text,
            condition=be.visible)

    def click(self):
        self._execute(
            lambda: self.__delegate__.click(),
            condition=be.visible)
        return self  # todo: think on: IWebElement#click was supposed to return None

    def submit(self):
        self._execute(
            lambda: self.__delegate__.submit(),
            condition=be.visible)
        return self

    def clear(self):
        self._execute(
            lambda: self.__delegate__.clear(),
            condition=be.visible)
        return self

    def get_attribute(self, name):
        return self._execute(
            lambda: self.__delegate__.get_attribute(name),
            condition=be.in_dom)

    def is_selected(self):
        return self._execute(
            lambda: self.__delegate__.is_selected(),
            condition=be.visible)

    def is_enabled(self):
        return self._execute(
            lambda: self.__delegate__.is_enabled(),
            condition=be.visible)

    def send_keys(self, *value):
        self._execute(
            lambda: self.__delegate__.send_keys(*value),
            condition=be.visible)
        return self

    # RenderedWebElement Items
    def is_displayed(self):
        return self._execute(
            lambda: self.__delegate__.is_displayed(),
            condition=be.in_dom)

    @property
    def location_once_scrolled_into_view(self):
        return self._execute(
            lambda: self.__delegate__.location_once_scrolled_into_view,
            condition=be.visible)

    @property
    def size(self):
        return self._execute(
            lambda: self.__delegate__.size,
            condition=be.visible)

    def value_of_css_property(self, property_name):
        return self._execute(
            lambda: self.__delegate__.value_of_css_property(property_name),
            condition=be.in_dom)

    @property
    def location(self):
        return self._execute(
            lambda: self.__delegate__.location,
            condition=be.visible)

    @property
    def rect(self):
        return self._execute(
            lambda: self.__delegate__.rect,
            condition=be.visible)

    @property
    def screenshot_as_base64(self):
        return self._execute(
            lambda: self.__delegate__.screenshot_as_base64,
            condition=be.visible)  # todo: or `be.in_dom`?

    @property
    def screenshot_as_png(self):
        return self._execute(
            lambda: self.__delegate__.screenshot_as_png,
            condition=be.visible)  # todo: or `be.in_dom`?

    def screenshot(self, filename):
        return self._execute(
            lambda: self.__delegate__.screenshot(filename),
            condition=be.visible)  # todo: or `be.in_dom`?

    @property
    def parent(self):
        return self._execute(
            lambda: self.__delegate__.parent,  # todo: should not we return here some Selene entity as search_context?
            condition=be.in_dom)

    @property
    def id(self):
        return self._execute(
            lambda: self.__delegate__.id,
            condition=be.in_dom)

    # *** private methods ***

    def _execute(self, command, condition=be.or_not_to_be):
        try:
            return command()
        except (WebDriverException,):
            self.should(condition)
            return command()


class SeleneCollection(Sequence):
    """
    To fully match Selenium, SeleneCollection should extend collection.abc.MutableSequence.
    But that's the place where we should be more restrictive.
    It is actually the Selenium, who should use "Sequence" instead of "MutableSequence" (list)
    """

    __metaclass__ = DelegatingMeta

    @property
    def __delegate__(self):
        # type: () -> List[IWebElement]
        return self._locator.find()

    def __call__(self):
        # type: () -> List[IWebElement]
        return self.__delegate__

    @classmethod
    def by(cls, by, webdriver, context=None):
        # type: (Tuple[str, str], IWebDriver, ISearchContext) -> SeleneCollection
        if not context:
            context = webdriver

        return SeleneCollection(SearchContextListWebElementLocator(by, context), webdriver)

    @classmethod
    def by_css(cls, css_selector, webdriver, context=None):
        # type: (str, IWebDriver, ISearchContext) -> SeleneCollection
        if not context:
            context = webdriver

        return SeleneCollection.by((By.CSS_SELECTOR, css_selector), webdriver, context)

    @classmethod
    def by_css_or_by(cls, css_selector_or_by, webdriver, context=None):
        if not context:
            context = webdriver

        return SeleneCollection.by(css_or_by_to_by(css_selector_or_by), webdriver, context)

    def __init__(self, selene_locator, webdriver):
        self._locator = selene_locator
        self._webdriver = webdriver

    def __str__(self):
        return self._locator.description

    # todo: consider extracting the following not DRY should methods to BaseMixin, or even better: some WaitObject
    # to be mixed in to both Selene Element and Collection
    # Points to think about:
    # * this may break DelegatingMeta logic (because we will have multiple inheritance...)
    # * this will Inheritance... Should not we at least use Composition here?
    def should(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        # todo: implement proper cashing
        # self._found = wait_for(self, condition, condition, timeout)
        wait_for(self, condition, condition, timeout)
        return self

    # todo: consider removing some aliases
    insist = should
    assure = should
    should_be = should
    should_have = should

    def should_not(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        # todo: implement proper cashing
        wait_for_not(self, condition, condition, timeout)
        return self

    # todo: consider removing some aliases are even all of them
    insist_not = should_not
    assure_not = should_not
    should_not_be = should_not
    should_not_have = should_not

    def should_each(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout

        for selement in self:
            selement.should(condition, timeout)

    def should_each_not(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout

        for selement in self:
            selement.should_not(condition, timeout)

    def filtered_by(self, condition):
        return SeleneCollection(FilteredListWebElementLocator(condition, self), self._webdriver)

    ss = filtered_by
    all_by = filtered_by
    filtered = filtered_by
    filter_by = filtered_by
    filterBy = filtered_by

    def element_by(self, condition):
        return SeleneElement(FoundByConditionWebElementLocator(condition, self), self._webdriver)

    s = element_by
    find_by = element_by
    findBy = element_by

    # *** Sequence methods ***

    def __getitem__(self, index):
        if isinstance(index, slice):
            return SeleneCollection(
                SlicedListWebElementLocator(index, collection=self),
                self._webdriver)
        return SeleneElement(IndexedWebElementLocator(index, collection=self), self._webdriver)

    def __len__(self):
        return len(self.__delegate__)

    # *** Overriden Sequence methods ***

    def __iter__(self):
        i = 0
        current_len = len(self)
        while i < current_len:
            v = self[i]
            yield v
            i += 1

    # *** Additional Collection style methods ***

    # *** Useful shortcuts ***

    def size(self):
        return len(self)

    def first(self):
        return self[0]

    # # *** private methods ***
    #
    # def _execute(self, command, condition=be.or_not_to_be):
    #     try:
    #         return command()
    #     except (WebDriverException,):
    #         self.should(condition)
    #         return command()


class IWebDriverSource(object):
    __metaclass__ = ABCMeta

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


class SeleneDriver(IWebDriver):
    __metaclass__ = DelegatingMeta

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