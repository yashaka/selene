from abc import abstractproperty, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selene.abctypes.search_context import ISearchContext


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

