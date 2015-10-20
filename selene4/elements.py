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

    def __getattr__(self, item):
        found = None
        try:
            found = self.finder()
        except WebDriverException:
            for condition in self.default_conditions:
                found = self.assure(condition)
        return getattr(found, item)

    def assure(self, condition):
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
        self.default_conditions = []

    def finder(self):
        return [self._wrapper_class(webelement, '%s[%s]' % (self.locator, index))
                for index, webelement in enumerate(self.context.find_elements_by_css_selector(self.locator))]

    def filter(self, condition):
        filtered_elements = [selement for selement in self.finder()
                             if condition(selement)]
        return SmartElementsCollectionWrapper(filtered_elements, self.locator + "[filtered by ...]") # todo: refactor to be verbose

    def find(self, condition_class, *condition_args):
        return self.filter(condition_class, *condition_args)[0]

    def assure_each(self, condition):
        """ asserts conditions on each its item """
        for selement in self:
            selement.assure(condition)
        return self

    def __getitem__(self, item):
        self.assure(size_at_least(item + 1))
        return self.finder().__getitem__(item)  # todo: think on fixing probable slowability :) because of additional finder() call

    def __len__(self):
        return self.finder().__len__()

    def __iter__(self):
        return self.finder().__iter__()

    def __getslice__(self, i, j):
        # todo: think on: should we pass here self._context, and self._wrapper_class into constructor?
        return SmartElementsCollectionWrapper(self.finder().__getslice__(i, j), self.locator + "[sliced by ...]")


class SmartElementsCollectionWrapper(SElementsCollection):
    def __init__(self, smart_elements_list, locator):
        self.wrapped_elements_list = smart_elements_list
        super(SmartElementsCollectionWrapper, self).__init__(locator)

    def finder(self):
        return self.wrapped_elements_list