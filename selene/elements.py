from selenium.webdriver.remote.webelement import WebElement
from selene import config
from selene.conditions import visible, not_empty, of_size
from selene.driver import browser
from selene.helpers import merge
from selene.page_object import Filler
from selene.waits import wait_for


class RootSElement(object):
    def __getattr__(self, item):
        return getattr(browser(), item)


class Container(object):
    def __init__(self):
        self.init()

    def init(self):
        """ to be defined in descendants in order to init its sub-elements """
        pass


class BaseFinder(object):

    def _finder(self):
        """ to be defined in descendants as a function to find itself (actually its wrapped WebElement) """
        pass

    def _open(self):
        """ a function to open self in case it should be somehow loaded to become visible """
        pass

    def to_open(self, how_to_open_fn):
        """ specifies the way to open self in case it should be explicitly loaded to become visible """
        self._open = how_to_open_fn
        return self

    def that(self, condition, *others):
        """ adds conditions to self to be asserted on it each time it will be used """
        self._conditions.extend([condition] + list(others))
        return self

    def _get(self):
        """ loads self via _open, asserts _conditions on it, and returns what was found by _finder
            i.e. = 'smart' _finder"""
        return wait_for(self._finder, until=self._conditions, after=self._open)

    def get(self):
        """ convenient method to load self explicitly before e.g. #insist that will not load by default """
        self._get()
        return self

    def insist(self, condition=visible, *others, **kwargs):
        """ asserts conditions on self
            by default it is forced to assert without self pre-loading if available via _open (kwargs['forced']=True) """
        opts = merge(dict(forced=True), kwargs)
        conditions = [condition] + list(others)

        acquire = self._finder if opts["forced"] else self._get

        wait_for(acquire, until=conditions)
        return self
        # todo: think on: is the #_get really needed here? maybe leave #_get only for everything except #insist?
        #       saying... Once you do something with element... you have a default checks and waits...
        #       but once you do insist it is assumed you know what you do...
        #       hm... From other point of view... such impl of insist makes #assure be defined in a DRY way...

    def assure(self, condition=visible, *others):
        """ alias to #insist with forced=False, i.e. leaving the element opportunity to load itself before assert
            i.e. = 'smart' insist """
        return self.insist(condition, *others, forced=False)


class SElement(Filler, BaseFinder, Container):

    def __init__(self, locator_or_element, context=RootSElement()):
        if type(locator_or_element) not in (str, WebElement):
            raise TypeError('Unknown element type for element_or_locator parameter. '
                            'Only WebElement and str are accepted')

        self._context = context

        self._conditions = [visible] if config.default_wait_selement_until_displayed else []

        if isinstance(locator_or_element, str):
            self._finder = lambda: self._context.find_element_by_css_selector(locator_or_element)
        elif isinstance(locator_or_element, WebElement):
            self._finder = lambda: locator_or_element
        # todo: think on refactoring the _finder definition to be more straightforward and maybe via fn instead of lambda

        super(SElement, self).__init__()

    def __getattr__(self, item):
        return getattr(self._get(), item)

    def set(self, value):
        self.send_keys(value)
        return self

    def within(self, context):
        """ conveniently sets context for self to be found in """
        self._context = context
        return self

    def s(self, locator_or_selement):
        """ convenient method to define sub-selements with context automatically set to self """
        if isinstance(locator_or_selement, SElement):
            return locator_or_selement.within(self)
        return SElement(locator_or_selement, self)

    def ss(self, locator):
        """ convenient method to define sub-selementscollections with context automatically set to self """
        return SElementsCollection(locator, self)

    # todo: redefine WebElement's methods like #click in order to return self in order to be used "in chain"


class SElementsCollection(BaseFinder, Container):
    def __init__(self, locator, context=RootSElement(), wrapper_class=SElement):
        self._context = context
        self._locator = locator
        self._wrapper_class = wrapper_class
        self._conditions = [not_empty] if config.default_wait_selist_until_is_not_empty else []
        self._each_conditions = [visible] if config.default_wait_selement_until_displayed else []

        super(SElementsCollection, self).__init__()

    def _finder(self):
        return [self._wrapper_class(webelement).insist(*self._each_conditions, forced=False)
                for webelement in self._context.find_elements_by_css_selector(self._locator)]

    def of(self, selement_class):
        """ sets _wrapper_class to wrap its 'items' in """
        self._wrapper_class = selement_class
        return self

    def each(self, condition, *others):
        """ adds conditions to self to be asserted on each its item each time it will be used """
        self._each_conditions.extend([condition] + list(others))
        return self

    def insist_each(self, condition, *others):
        """ asserts conditions on each its item """
        for selement in self:
            selement.insist(condition, *others)
        return self

    def __getattr__(self, item):
        return getattr(self._get(), item)

    def __getitem__(self, item):
        return self._get().__getitem__(item)

    def __len__(self):
        return self._get().__len__()

    def __iter__(self):
        return self._get().__iter__()

    # todo: automate proxying all other magic methods (http://code.activestate.com/recipes/496741-object-proxying/)
    # todo: or proxy them explicitly if better
