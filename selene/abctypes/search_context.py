from abc import ABCMeta, abstractmethod
from _ast import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


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