"""The Selene's WebDriver Decorator implementation."""
from _ast import List
from _ast import Tuple
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Sequence

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selene.conditions import Condition
from selene.support.conditions import be
from selene.support.conditions import have
from core.delegation import DelegatingMeta
from selene import config
from selene.wait import wait_for, wait_for_not


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
        self._search_context.find_elements(*self._by)


class FilteredListWebElementLocator(ISeleneListWebElementLocator):
    def find(self):
        return [selement()
                for selement in self._collection
                if self._condition(selement)]

    @property
    def description(self):
        return "By.Selene: (%s).filter_by(%s)" % (self._collection, self._condition)

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


class FoundByConditionWebElementLocator(ISeleneWebElementLocator):
    def find(self):
        for selement in self._collection:
            if self._condition(selement):
                return selement()

    @property
    def description(self):
        return "By.Selene: (%s).find_by(%s)" % (self._collection, self._condition)

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


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
        # type: (Tuple[str, str], WebDriver, ISearchContext) -> SeleneElement
        if not context:
            context = webdriver

        return SeleneElement(SearchContextWebElementLocator(by, context), webdriver)

    @classmethod
    def by_css(cls, css_selector, webdriver, context=None):
        # type: (str, WebDriver, ISearchContext) -> SeleneElement
        if not context:
            context = webdriver

        return SeleneElement.by((By.CSS_SELECTOR, css_selector), webdriver, context)

    @classmethod
    def by_css_or_by(cls, css_selector_or_by, webdriver, context=None):
        if not context:
            context = webdriver

        # todo: will it work `if isinstance(css_selector_or_by, Tuple[str, str]):` ?
        if isinstance(css_selector_or_by, tuple):
            return SeleneElement.by(css_selector_or_by, webdriver, context)
        if isinstance(css_selector_or_by, str):
            return SeleneElement.by_css(css_selector_or_by, webdriver, context)
        raise TypeError('css_selector_or_by should be str with CSS selector or Tuple[by:str, value:str]')

    def __init__(self, selene_locator, webdriver):
        # type: (ISeleneWebElementLocator, WebDriver) -> None
        self._locator = selene_locator
        self._webdriver = webdriver
        self._actions_chains = ActionChains(webdriver)

    def __str__(self):
        return self._locator.description

    def s(self, css_selector_or_by):
        return SeleneElement.by_css_or_by(css_selector_or_by, self._webdriver, context=self)

    element = s
    find = s

    def ss(self, css_selector_or_by):
        return SeleneCollection.by_css_or_by(css_selector_or_by, self._webdriver, context=self)

    all = ss
    elements = ss
    find_all = ss

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
        return self._webdriver.find_elements(by, value)

    def find_element(self, by=By.ID, value=None):
        return self._webdriver.find_element(by, value)

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
        # type: (Tuple[str, str], WebDriver, ISearchContext) -> SeleneCollection
        if not context:
            context = webdriver

        return SeleneCollection(SearchContextListWebElementLocator(by, webdriver), webdriver)

    @classmethod
    def by_css(cls, css_selector, webdriver, context=None):
        # type: (str, WebDriver, ISearchContext) -> SeleneCollection
        if not context:
            context = webdriver

        return SeleneCollection.by((By.CSS_SELECTOR, css_selector), webdriver, context)

    @classmethod
    def by_css_or_by(cls, css_selector_or_by, webdriver, context=None):
        if not context:
            context = webdriver

        if isinstance(css_selector_or_by, tuple):
            return SeleneCollection.by(css_selector_or_by, webdriver, context)
        if isinstance(css_selector_or_by, str):
            return SeleneCollection.by_css(css_selector_or_by, webdriver, context)
        raise TypeError('css_selector_or_by should be str with CSS selector or Tuple[by:str, value:str]')

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

    def ss(self, condition):
        return SeleneCollection(FilteredListWebElementLocator(condition, self), self._webdriver)

    filtered = ss
    all_by = ss
    filter_by = ss

    def s(self, condition):
        return SeleneCollection(FoundByConditionWebElementLocator(condition, self), self._webdriver)

    element_by = s
    find_by = s

    # *** Sequence methods ***

    def __getitem__(self, index):
        return SeleneCollection(IndexedWebElementLocator(index, collection=self), self._webdriver)

    def __len__(self):
        return len(self.__delegate__)

    # *** Overriden Sequence methods ***

    def __iter__(self):
        i = 0
        current_len = len(self)
        while i <= current_len:
            v = self[i]
            yield v
            i += 1

    # *** Useful shortcuts ***

    def size(self):
        return len(self)

    def first(self):
        return self[0]


class SeleneDriver(ISearchContext):
    def __init__(self, webdriver):
        self._webdriver = webdriver

    def s(self, css_selector_or_by):
        return SeleneElement.by_css_or_by(css_selector_or_by, self._webdriver)

    element = s
    find = s

    def ss(self, css_selector_or_by):
        return SeleneCollection.by_css_or_by(css_selector_or_by, self._webdriver)

    all = ss
    elements = ss
    find_all = ss

    # *** SearchContext methods ***
    def find_elements(self, by=By.ID, value=None):
        # return self._webdriver.find_elements(by, value)
        return self.find_all((by, value))

    def find_element(self, by=By.ID, value=None):
        # return self._webdriver.find_element(by, value)
        return self.find((by, value))
