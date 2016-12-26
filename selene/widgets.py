from selenium.webdriver.support.select import Select

from selene.conditions import visible
from selene.elements import RootSElement, SElement


class SelectList(SElement):
    def __init__(self, locator, context=RootSElement()):
        super(SelectList, self).__init__(locator, context)

    def set(self, value):
        self.assure(visible)  # todo: how to improve? - seems like custom selements should be implemented with manual AJAX handling...
        # todo: think on: refactoring based on inspirations from capybara's `#select` implementation
        Select(self.found).select_by_visible_text(value)
        return self