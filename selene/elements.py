from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from conditions import *
from selene import config
from selene.bys import by_css
from selene.page_object import Filler, LoadableContainer
from selene.wait import wait_for, wait_for_not


def actions():
    return ActionChains(config.driver)


class WaitingFinder(object):

    def __init__(self):
        self.is_cached = False
        self._found = None
        self._default_conditions = []

    def that(self, *default_conditions):
        self._default_conditions = default_conditions
        return self

    def _finder(self):
        pass

    # todo: consider making it public, because it is used outside of this class (in SElementsCollection)
    def _cash_with(self, found_entity):
        self.is_cached = True
        self._finder = lambda: found_entity
        return self

    def _refind(self):
        self._found = self._finder()
        if config.cash_elements:
            self._cash_with(self.found)
        return self._found

    @property
    def found(self):
        if not self._found:
            self._refind()
        return self._found

    # @found.setter
    # def found(self, found_element):
    #     self._found = found_element

    def cash(self):
        self._cash_with(self.found)
        return self

    # todo: is used outside of class... should we make it public? :)...
    #       or find another way to reach the goal outside of the class
    def _execute(self, command, conditions = None):
        if not conditions:
            conditions = self._default_conditions
        """
        :param command: command operated on self.found
        :return: result returned by command
        """
        result = None
        try:
            if not self.is_cached:  # todo: maybe move this check into _find?
                self._refind()
            result = command()
        except (WebDriverException, IndexError):  # todo: consider `except self.handled_exceptions`
            for condition in conditions:
                self.assure(condition)  # todo: wait for "default condition" not visible
            result = command()
        return result

    def _do(self, command):
        """
        :param command: command operated on self.found
        :return: self
        """
        self._execute(command)
        return self

    # do we actually need this method?
    def __call__(self):
        """
        :return: re-found wrapped entity
        """
        return self._refind()

    # todo: consider removing it completely after mapping all webelement methods
    def __getattr__(self, item):
        return self._execute(lambda: getattr(self.found, item))

    # todo: refactor caching logic in case of assure
    # if entity is cached assure will wait for nothing...
    # what is actually needed in "cached case"
    # is making all element actions on cached version
    # and also do first check in waiting assure - on cached version
    # but once this "first check" failed - it's pretty reasonable "update" cash
    #
    # the same relates to assure_not of course
    def assure(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        self._found = wait_for(self, condition, condition, timeout)
        return self

    insist = assure
    should = assure
    should_be = assure
    should_have = assure

    def assure_not(self, condition, timeout=None):
        if not timeout:
            timeout = config.timeout
        # todo: where is self._found = ?          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        wait_for_not(self, condition, condition, timeout)
        return self

    insist_not = assure_not
    should_not = assure_not
    should_not_be = assure_not
    should_not_have = assure_not

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


# todo: think... with this multiple inheritance all the time
#       I forget to set some field of some parent during refactoring...
#       how to improve? o_O
class SElement(LoadableContainer, WaitingFinder, Filler):
    def __init__(self, css_selector_or_locator, context=RootSElement()):
        self.locator = parse_css_or_locator_to_tuple(css_selector_or_locator)
        self.context = context
        self._default_conditions = [visible]
        self.is_cached = False
        self._found = None
        super(SElement, self).__init__()

    def _finder(self):
        return self.context.find_element(*self.locator)

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
        return self._do(lambda: self.found.click())

    def double_click(self):
        return self._do(lambda: actions().double_click(self.found).perform())

    def set(self, new_text_value):

        def clear_and_send_keys():
            self.found.clear()
            self.found.send_keys(new_text_value)

        return self._do(clear_and_send_keys)

    set_value = set

    def send_keys(self, *keys):
        return self._do(lambda: self.found.send_keys(*keys))

    def press_enter(self):
        return self._do(lambda: self.found.send_keys(Keys.ENTER))

    def press_escape(self):
        return self._do(lambda: self.found.send_keys(Keys.ESCAPE))

    def hover(self):
        return self._do(lambda: actions().move_to_element(self.found).perform())


class Wrapper(object):
    """ to be used as marker for classes for objects
    that do not need waiting during '__getattr__' """
    pass

# todo: do we even need it? taking into acouunt that we can cash element to get the same _finder implementation...
class SElementWrapper(SElement, Wrapper):
    def __init__(self, selement, locator=None):
        self._wrapped_element = selement
        super(SElementWrapper, self).__init__(locator or selement.locator)

    def _finder(self):
        return self._wrapped_element


class SElementsCollection(LoadableContainer, WaitingFinder):
    def __init__(self, css_selector_or_locator, context=RootSElement(), selement_class=SElement):
        self.locator = parse_css_or_locator_to_tuple(css_selector_or_locator)
        self.context = context
        self._wrapper_class = selement_class
        self._default_conditions = []
        self._found = None
        self.is_cached = False
        super(SElementsCollection, self).__init__()

    def of(self, selement_class):
        self._wrapper_class = selement_class
        return self

    def within(self, context):
        self.context = context
        return self

    def _finder(self):
        return [self._wrapper_class('%s[%s]' % (self.locator, index))._cash_with(webelement)
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
        return self._execute(lambda: self.found.__len__())

    def __iter__(self):
        return self._execute(lambda: self.found.__iter__())

    def __getslice__(self, i, j):
        # todo: think on: should we pass here self._context, and self._wrapper_class into constructor?
        return SlicedSElementsCollection(self, i, j)


class SElementsCollectionWrapper(SElementsCollection, Wrapper):
    def __init__(self, selements_list, css_selector_or_locator):
        self.wrapped_elements_list = selements_list
        super(SElementsCollectionWrapper, self).__init__(css_selector_or_locator)

    def _finder(self):
        return self.wrapped_elements_list


class SElementsCollectionElement(SElement, Wrapper):
    def __init__(self, selements_collection, index):
        self.index = index
        self.selements_collection = selements_collection
        locator = "%s[%s]" % (self.selements_collection.locator, self.index)
        super(SElementsCollectionElement, self).__init__(("selene", locator))

    def _finder(self):
        # todo: consider move `.that(size_at_least(self.index + 1))` to `_execute(lambda: ..., size_at_least(...))`
        element_by_index = self.selements_collection._execute(lambda: self.selements_collection.that(size_at_least(self.index + 1)).found[self.index])
        return SElementWrapper(element_by_index,
                               self.locator)


class SlicedSElementsCollection(SElementsCollection, Wrapper):
    # todo: rename i & j to something more informative
    def __init__(self, original_selements_collection, i, j):
        self.i = i
        self.j = j
        self.selements_collection = original_selements_collection
        locator = "%s[%s:%s]" % (self.selements_collection.locator, self.i, self.j)
        super(SlicedSElementsCollection, self).__init__(("selene", locator))

    def _finder(self):
        sliced_elements = self.selements_collection._execute(lambda: self.selements_collection.that(size_at_least(self.j)).found[self.i:self.j])
        return SElementsCollectionWrapper(sliced_elements, self.locator)

class FilteredSElementsCollection(SElementsCollection, Wrapper):
    def __init__(self, original_selements_collection, condition):
        self.original_selements_collection = original_selements_collection
        self.condition = condition
        locator = "(%s).filter(%s)" % (
            self.original_selements_collection.locator,
            self.condition.__class__.__name__)
        super(FilteredSElementsCollection, self).__init__(("selene", locator)) # todo: prettify and fix it in other similiar places, it's not a css selector to be passed as string

    def _finder(self):
        filtered_elements = [selement for selement in self.original_selements_collection
                             if self.condition(selement)]
        return SElementsCollectionWrapper(
            filtered_elements,
            self.locator)
