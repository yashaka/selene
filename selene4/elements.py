from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from conditions import *
from selene4 import config
from selene4.wait import wait_for


def actions():
    return ActionChains(config.driver)


class WaitingFinder(object):

    def __init__(self):
        self.locator = None
        self.default_conditions = []

    def finder(self):
        pass

    def __call__(self):
        return self.finder()

    def __getattr__(self, item):
        found = None
        try:
            found = self.finder()
        except WebDriverException:
            for condition in self.default_conditions:
                found = self.assure(condition)
        return getattr(found, item)

    def assure(self, condition, timeout=config.timeout):
        wait_for(self, condition, condition)
        return self

    def __str__(self):
        return self.locator


class RootSElement(object):
    def __getattr__(self, item):
        return getattr(config.driver, item)


class SElement(WaitingFinder):
    def __init__(self, css_selector, context=RootSElement()):
        self.locator = css_selector
        self.context = context
        self.default_conditions = [visible]

    def finder(self):
        return self.context.find_element_by_css_selector(self.locator)

    def within(self, context):
        self.context = context
        return self

    def s(self, css_locator):
        return SElement(css_locator, self)

    def ss(self, css_locator):
        return SElementsCollection(css_locator, self)

    def double_click(self):
        actions().double_click(self).perform()
        return self

    def set_value(self, new_text_value):
        self.clear()
        self.send_keys(new_text_value)
        return self

    def press_enter(self):
        self.send_keys(Keys.ENTER)
        return self

    def hover(self):
        actions().move_to_element(self).perform()
        return self


class SElementWrapper(SElement):
    def __init__(self, smart_element, locator=None):
        self._wrapped_element = smart_element
        super(SElementWrapper, self).__init__(locator or smart_element.locator)

    def finder(self):
        return self._wrapped_element


class SElementsCollection(WaitingFinder):
    def __init__(self, css_selector, context=RootSElement(), wrapper_class=SElementWrapper):
        self.locator = css_selector
        self.context = context
        self._wrapper_class = wrapper_class

    def finder(self):
        return [self._wrapper_class(webelement, '%s[%s]' % (self.locator, index))
                for index, webelement in enumerate(self.context.find_elements_by_css_selector(self.locator))]

    def filter(self, condition):
        return FilteredSElementsCollection(self, condition)

    def find(self, condition_class, *condition_args):
        return self.filter(condition_class, *condition_args)[0]

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
        return SElementsCollectionWrapper(self.finder().__getslice__(i, j), self.locator + "[sliced by ...]")


class SElementsCollectionWrapper(SElementsCollection):
    def __init__(self, smart_elements_list, locator):
        self.wrapped_elements_list = smart_elements_list
        super(SElementsCollectionWrapper, self).__init__(locator)

    def finder(self):
        return self.wrapped_elements_list

class SElementsCollectionElement(SElement):
    def __init__(self, selements_collection, index):
        self.index = index
        self.selements_collection = selements_collection

    def finder(self):
        self.selements_collection.assure(size_at_least(self.index + 1))
        return SElementWrapper(self.selements_collection.finder()[self.index],
                               "%s[%s]" % (self.selements_collection.locator, self.index))

class FilteredSElementsCollection(SElementsCollection):
    def __init__(self, original_selements_collection, condition):
        self.original_selements_collection = original_selements_collection
        self.condition = condition

    def finder(self):
        filtered_elements = [selement for selement in self.original_selements_collection
                             if self.condition(selement)]
        return SElementsCollectionWrapper(
            filtered_elements,
            "(%s).filter(%s)" % (
                self.original_selements_collection.locator,
                self.condition.__class__.__name__))
