from _ast import Tuple, List
from collections import Sequence

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selene import config
from selene.abctypes.locators import ISeleneWebElementLocator, ISeleneListWebElementLocator
from selene.abctypes.search_context import ISearchContext
from selene.abctypes.webdriver import IWebDriver
from selene.abctypes.webelement import IWebElement
from selene.conditions import Condition, not_
from selene.common.delegation import DelegatingMeta
from selene.helpers import css_or_by_to_by
from selene.support import by
from selene.support.conditions import be
from selene.support.conditions import have
from selene.wait import wait_for

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


# todo: consider renaming/refactoring to WebDriverWebElementLocator...
class WebDriverWebElementLocator(ISeleneWebElementLocator):
    def __init__(self, by, search_context):
        # type: (Tuple[By, str], ISearchContext) -> None
        self._by = by
        self._search_context = search_context

    @property
    def description(self):
        return 'first_by%s' % str(self._by)

    def find(self):
        return self._search_context.find_element(*self._by)


class InnerWebElementLocator(ISeleneWebElementLocator):
    def __init__(self, by, element):
        # type: (Tuple[By, str], SeleneElement) -> None
        self._by = by
        self._element = element

    @property
    def description(self):
        return "%s.find_by%s" % (self._element, self._by)

    def find(self):
        return self._element.get_actual_webelement().find_element(*self._by)


class CachingWebElementLocator(ISeleneWebElementLocator):
    @property
    def description(self):
        return "Caching %s" % (self._element,)

    @lru_cache()
    def find(self):
        return self._element()

    def __init__(self, element):
        self._element = element


# todo: PyCharm generates abstract methods impl before __init__ method.
# todo: Should we use this order convention? like below...
class IndexedWebElementLocator(ISeleneWebElementLocator):
    def find(self):
        return self._collection.get_actual_webelements()[self._index]

    @property
    def description(self):
        return "%s[%s]" % (self._collection, self._index)

    def __init__(self, index, collection):
        # type: (int, SeleneCollection) -> None
        self._index = index
        self._collection = collection


class WebdriverListWebElementLocator(ISeleneListWebElementLocator):
    def __init__(self, by, search_context):
        # type: (Tuple[By, str], ISearchContext) -> None
        self._by = by
        self._search_context = search_context

    @property
    def description(self):
        return 'all_by%s' % str(self._by)

    def find(self):
        return self._search_context.find_elements(*self._by)


class InnerListWebElementLocator(ISeleneListWebElementLocator):
    def __init__(self, by, element):
        # type: (Tuple[By, str], SeleneElement) -> None
        self._by = by
        self._element = element

    @property
    def description(self):
        return "(%s).find_all_by(%s)" % (self._element, self._by)

    def find(self):
        return self._element.get_actual_webelement().find_elements(*self._by)


class FilteredListWebElementLocator(ISeleneListWebElementLocator):
    def find(self):
        webelements = self._collection()
        filtered = [webelement
                    for webelement in webelements
                    if self._condition.matches_webelement(webelement)]
        return filtered

    @property
    def description(self):
        return "(%s).filter_by(%s)" % (self._collection, self._condition.description())

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


class SlicedListWebElementLocator(ISeleneListWebElementLocator):
    def find(self):
        # self._collection.should(have.size_at_least(self._slice.stop)) # todo: remove once covered with tests
        webelements = self._collection()
        return webelements[self._slice.start:self._slice.stop:self._slice.step]

    @property
    def description(self):
        return "(%s)[%s:%s:%s]" % (self._collection, self._slice.start, self._slice.stop, self._slice.step)

    def __init__(self, slc,  collection):
        # type: (slice, SeleneCollection) -> None
        self._slice = slc
        self._collection = collection


class FoundByConditionWebElementLocator(ISeleneWebElementLocator):
    def find(self):
        for webelement in self._collection():
            if self._condition.matches_webelement(webelement):
                return webelement
        raise NoSuchElementException('Element was not found by: %s' % (self._condition,))

    @property
    def description(self):
        return "(%s).select_by(%s)" % (self._collection, self._condition.description())

    def __init__(self, condition, collection):
        # type: (Condition, SeleneCollection) -> None
        self._condition = condition
        self._collection = collection


class SeleneElement(IWebElement):
    __metaclass__ = DelegatingMeta

    @property
    def __delegate__(self):
        # type: () -> IWebElement
        return self._locator.find()

    # todo: is this alias needed?
    def get_actual_webelement(self):
        # type: () -> IWebElement
        return self.__delegate__

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

        return SeleneElement(WebDriverWebElementLocator(by, context), webdriver)

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
        # type: (ISeleneWebElementLocator, IWebDriver) -> None
        self._locator = selene_locator
        self._webdriver = webdriver
        self._actions_chains = ActionChains(webdriver)

    def __str__(self):
        return self._locator.description

    # *** Relative elements ***

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

    @property
    def parent_element(self):
        return self.element(by.be_parent())

    @property
    def following_sibling(self):
        return self.element(by.be_following_sibling())

    @property
    def first_child(self):
        return self.element(by.be_first_child())

    # *** Asserts (Explicit waits) ***

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
        not_condition = not_(condition)
        wait_for(self, not_condition, not_condition, timeout)
        return self

    # todo: consider removing some aliases
    insist_not = should_not
    assure_not = should_not
    should_not_be = should_not
    should_not_have = should_not

    # *** Additional actions ***

    def double_click(self):
        self._execute(
            lambda: self._actions_chains.double_click(self.__delegate__).perform(),
            condition=be.Visible())
        return self

    def set(self, new_text_value):

        def clear_and_send_keys():
            self.__delegate__.clear()
            self.__delegate__.send_keys(new_text_value)

        self._execute(
            clear_and_send_keys,
            condition=be.Visible())

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
            condition=be.Visible())
        return self

    # *** ISearchContext methods ***

    def find_elements(self, by=By.ID, value=None):
        return self._execute(
            lambda: self.__delegate__.find_elements(by, value),
            condition=be.Visible())
        # return self.__delegate__.find_elements(by, value) # todo: remove

    def find_element(self, by=By.ID, value=None):
        return self._execute(
            lambda: self.__delegate__.find_element(by, value),
            condition=be.Visible())
        # return self.__delegate__.find_element(by, value) # todo: remove

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
            condition=be.Visible())

    def click(self):
        self._execute(
            lambda: self.__delegate__.click(),
            condition=be.Visible())
        return self  # todo: think on: IWebElement#click was supposed to return None

    def submit(self):
        self._execute(
            lambda: self.__delegate__.submit(),
            condition=be.Visible())
        return self

    def clear(self):
        self._execute(
            lambda: self.__delegate__.clear(),
            condition=be.Visible())
        return self

    def get_attribute(self, name):
        return self._execute(
            lambda: self.__delegate__.get_attribute(name),
            condition=be.in_dom)

    def is_selected(self):
        return self._execute(
            lambda: self.__delegate__.is_selected(),
            condition=be.Visible())

    def is_enabled(self):
        return self._execute(
            lambda: self.__delegate__.is_enabled(),
            condition=be.Visible())

    def send_keys(self, *value):
        self._execute(
            lambda: self.__delegate__.send_keys(*value),
            condition=be.Visible())
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
            condition=be.Visible())

    @property
    def size(self):
        return self._execute(
            lambda: self.__delegate__.size,
            condition=be.Visible())

    def value_of_css_property(self, property_name):
        return self._execute(
            lambda: self.__delegate__.value_of_css_property(property_name),
            condition=be.in_dom)

    @property
    def location(self):
        return self._execute(
            lambda: self.__delegate__.location,
            condition=be.Visible())

    @property
    def rect(self):
        return self._execute(
            lambda: self.__delegate__.rect,
            condition=be.Visible())

    @property
    def screenshot_as_base64(self):
        return self._execute(
            lambda: self.__delegate__.screenshot_as_base64,
            condition=be.Visible())  # todo: or `be.in_dom`?

    @property
    def screenshot_as_png(self):
        return self._execute(
            lambda: self.__delegate__.screenshot_as_png,
            condition=be.Visible())  # todo: or `be.in_dom`?

    def screenshot(self, filename):
        return self._execute(
            lambda: self.__delegate__.screenshot(filename),
            condition=be.Visible())  # todo: or `be.in_dom`?

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
        except Exception:
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

    def get_actual_webelements(self):
        # type: () -> List[IWebElement]
        return self.__delegate__

    def __call__(self):
        # type: () -> List[IWebElement]
        return self.__delegate__

    @classmethod
    def by(cls, by, webdriver, context=None):
        # type: (Tuple[str, str], IWebDriver, ISearchContext) -> SeleneCollection
        if not context:
            context = webdriver

        return SeleneCollection(WebdriverListWebElementLocator(by, context), webdriver)

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
        # type: (ISeleneListWebElementLocator, IWebDriver) -> None
        self._locator = selene_locator
        self._webdriver = webdriver

    # todo: consider adding self.cashing, self.cashed - like for SeleneElement

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
        not_condition = not_(condition)
        wait_for(self, not_condition, not_condition, timeout)
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
        # todo: optimise to the following:
        #   return self.waifFor(size_at_least(0)),
        # where waitFor will return the result of condition application, not self like should
        self.should(have.size_at_least(0))
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
