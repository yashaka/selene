import os

EMPTY_PAGE_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/empty.html'


class LoadingHtmlPage(object):

    def __init__(self, timeout=0, body=""):
        self._body = body
        self._timeout = timeout

    def load_in(self, driver):
        driver.get(EMPTY_PAGE_URL)
        return LoadedHtmlPage(driver).render_body(self._body, self._timeout)


class LoadedHtmlPage(object):
    def __init__(self, driver):
        self._driver = driver

    def render_body(self, body, timeout=0):
        self._driver.execute_script(
            'setTimeout(function() { document.getElementsByTagName("body")[0].innerHTML = "'
            + body.replace("\n", " ").replace('"', '\\"') + '";}, ' + str(timeout) + ");")
        return self

    def execute_script(self, script):
        self._driver.execute_script(script)
        return self

    def execute_script_with_timeout(self, script, timeout):
        self._driver.execute_script(
            "setTimeout(function() { " + script.replace("\n", " ") + " }, " + str(timeout) + ");")
        return self

    def render_body_with_timeout(self, body, timeout):
        return self.render_body(body, timeout)


class GivenPage(object):

    def __init__(self, driver):
        self._driver = driver

    def load_body_with_timeout(self, body, timeout):
        return LoadedHtmlPage(self._driver).render_body_with_timeout(body, timeout)

    def opened_with_body_with_timeout(self, body, timeout):
        return LoadingHtmlPage(timeout, body).load_in(self._driver)

    def opened_with_body(self, body):
        return self.opened_with_body_with_timeout(body, 0)

    def opened_empty(self):
        return LoadingHtmlPage().load_in(self._driver)

    def load_body(self, body):
        return LoadedHtmlPage(self._driver).render_body(body)
