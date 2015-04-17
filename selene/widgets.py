from selenium.webdriver.support.select import Select
from selene.elements import RootSElement, SElement


class SelectList(SElement):
    def __init__(self, locator, context=RootSElement()):
        super(SelectList, self).__init__(locator, context)

    def set(self, value):
        # todo: think on: refactoring based on inspirations from capybara's `#select` implementation
        Select(self._get()).select_by_visible_text(value)
        return self