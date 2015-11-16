from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from selene.elements import RootSElement, SElement


class SelectList(SElement):
    def __init__(self, locator, by=By.CSS_SELECTOR, context=RootSElement()):
        super(SelectList, self).__init__(locator, by, context)

    def set(self, value):
        # todo: think on: refactoring based on inspirations from capybara's `#select` implementation
        Select(self.find()).select_by_visible_text(value)
        return self