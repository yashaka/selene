from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from conditions import *
from selene import config
from selene.bys import by_css
from selene.page_object import Filler, Container
from selene.wait import wait_for, wait_for_not


def actions():
    return ActionChains(config.driver)


class WaitingFinder(object):

    def finder(self):
        pass

    def __call__(self):
        return self.finder()

    def __getattr__(self, item):
        if isinstance(self, Wrapper):
            self.found = self.finder()
        else:
            try:  # todo: do we even need this try here? is it probable to get fail here while need waiting?
                self.found = self.finder()  # todo: refactor: duplicates previous self.finder() call (though this duplication is in other context...)
            except WebDriverException:
                pass # todo: solve & finalize: seems like next line is not needed here... so all try can be removed...
                # self.assure(exist)  # todo: solve: it's general finder, but behaves like "Element" finder here, not like ElementsCollection finder...


        return getattr(self.found, item)

    def assure(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        self.found = wait_for(self, condition, condition, timeout)
        # self.found = self.finder() # todo: duplicated?
        return self

    insist = assure
    should = assure
    should_be = assure
    should_have = assure

    def assure_not(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        wait_for_not(self, condition, condition, timeout)
        return self

    def __str__(self):
        return str(self.locator)


class RootSElement(object):
    def __getattr__(self, item):
        return getattr(config.driver, item)


def parse_css_or_locator_to_tuple(css_selector_or_locator):
    if isinstance(css_selector_or_locator, str):
        return by_css(css_selector_or_locator)
    if isinstance(css_selector_or_locator, tuple):
        return css_selector_or_locator
    raise TypeError("s argument should be string or tuple!")


class SElement(Container, WaitingFinder, Filler):
    def __init__(self, css_selector_or_locator, context=RootSElement()):
        self.locator = parse_css_or_locator_to_tuple(css_selector_or_locator)
        self.context = context
        self.default_conditions = [visible]
        super(SElement, self).__init__()

    def finder(self):
        return self.context.find_element(*self.locator)

    def cash(self, found_element):
        self.finder = lambda: found_element
        return self

    def within(self, context):
        self.context = context
        return self

    # todo: consider passing second of=SElement parameter
    def s(self, css_selector_or_locator):
        return SElement(css_selector_or_locator).within(self)

    find = s

    def ss(self, css_selector_or_locator):
        return SElementsCollection(css_selector_or_locator).within(self)

    find_all = ss

    def click(self):
        self.assure(visible)
        self.found.click()
        return self

    def double_click(self):
        self.assure(visible)
        actions().double_click(self.found).perform()
        return self

    def set(self, new_text_value):
        self.assure(visible)
        self.found.clear()
        self.found.send_keys(new_text_value)
        return self

    set_value = set

    def send_keys(self, *keys):
        self.assure(visible)
        self.found.send_keys(*keys)
        return self

    def press_enter(self):
        return self.send_keys(Keys.ENTER)

    def press_escape(self):
        return self.send_keys(Keys.ESCAPE)

    def hover(self):
        self.assure(visible)
        actions().move_to_element(self.found).perform()
        return self


class Wrapper(object):
    """ to be used as marker for classes for objects
    that do not need waiting during '__getattr__' """
    pass

class SElementWrapper(SElement, Wrapper):
    def __init__(self, selement, locator=None):
        self._wrapped_element = selement
        super(SElementWrapper, self).__init__(locator or selement.locator)

    def finder(self):
        return self._wrapped_element


class SElementsCollection(WaitingFinder):
    def __init__(self, css_selector_or_locator, context=RootSElement(), selement_class=SElement):
        self.locator = parse_css_or_locator_to_tuple(css_selector_or_locator)
        self.context = context
        self._wrapper_class = selement_class
        self.default_conditions = []

    def of(self, selement_class):
        self._wrapper_class = selement_class
        return self

    def within(self, context):
        self.context = context
        return self

    def finder(self):
        return [self._wrapper_class('%s[%s]' % (self.locator, index)).cash(webelement)
                for index, webelement in enumerate(self.context.find_elements(*self.locator))]

    def filter(self, condition):
        return FilteredSElementsCollection(self, condition)

    filterBy = filter

    # todo: optimize it to find the only first, not all, and then get first.
    def find(self, condition):
        return self.filter(condition)[0]

    findBy = find

    def assure_each(self, condition):
        """ asserts conditions on each its item """
        for selement in self:
            selement.assure(condition)
        return self

    def __getitem__(self, item):
        return SElementsCollectionElement(self, item)

    def __len__(self):
        return self.finder().__len__()

    def __iter__(self):
        return self.finder().__iter__()

    def __getslice__(self, i, j):
        # todo: think on: should we pass here self._context, and self._wrapper_class into constructor?
        self.wrapper = SElementsCollectionWrapper(self.finder().__getslice__(i, j),
                                                  str(self.locator) + "[sliced by (%s, %s)]" % (i, j))
        return self.wrapper


class SElementsCollectionWrapper(SElementsCollection, Wrapper):
    def __init__(self, selements_list, css_selector_or_locator):
        self.wrapped_elements_list = selements_list
        super(SElementsCollectionWrapper, self).__init__(css_selector_or_locator)

    def finder(self):
        return self.wrapped_elements_list


class SElementsCollectionElement(SElement, Wrapper):
    def __init__(self, selements_collection, index):
        self.index = index
        self.selements_collection = selements_collection
        locator = "%s[%s]" % (self.selements_collection.locator, self.index)
        super(SElementsCollectionElement, self).__init__(("selene", locator))

    def finder(self):
        self.selements_collection.assure(size_at_least(self.index + 1))
        # return SElementWrapper(self.selements_collection.finder()[self.index],
        # return SElementWrapper(self.selements_collection.found[self.index],
        #                        self.locator)
        return SElementWrapper(self.selements_collection.found[self.index],
                               self.locator)


class FilteredSElementsCollection(SElementsCollection, Wrapper):
    def __init__(self, original_selements_collection, condition):
        self.original_selements_collection = original_selements_collection
        self.condition = condition
        locator = "(%s).filter(%s)" % (
            self.original_selements_collection.locator,
            self.condition.__class__.__name__)
        super(FilteredSElementsCollection, self).__init__(("selene", locator)) # todo: prettify and fix it in other similiar places, it's not a css selector to be passed as string

    def finder(self):
        filtered_elements = [selement for selement in self.original_selements_collection
                             if self.condition(selement)]
        return SElementsCollectionWrapper(
            filtered_elements,
            self.locator)
