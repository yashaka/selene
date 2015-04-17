from selenium import webdriver

# This is a fast draft implementation and should be enhanced...

class Browser(object):
    def __init__(self):
        self._driver = None

    def __del__(self):
        if self._driver:
            self._driver.quit()

    def __getattr__(self, item):
        return getattr(self._driver, item)

    def is_alive(self):
        # todo: implement
        return self._driver is not None

    def get_browser(self):
        if not self._driver or not self.is_alive():
            self._driver = webdriver.Firefox()
        return self._driver


# todo: consider refactoring to use static factory method of Browser class
_browser = Browser()


def browser():
    return _browser.get_browser()