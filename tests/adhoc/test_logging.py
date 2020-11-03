from selene.support.shared import browser
from selene import have, be


class TestOuterHtmlLogging:

    def test_one_element_enabled_logging(self):
        browser.config.log_outer_html = True
        browser.open('http://todomvc.com/examples/emberjs/')

        message = None
        try:
            browser.element('#new-todo').should(have.attribute('wrong_attr'))
        except Exception as e:
            message = str(e)

        assert message is not None
        assert message.find('Actual webelement:') != -1

    def test_one_element_disabled_logging(self):

        browser.config.log_outer_html = False
        browser.open('http://todomvc.com/examples/emberjs/')

        message = None
        try:
            browser.element('#new-todo').should(have.attribute('wrong_attr'))
        except Exception as e:
            message = str(e)

        assert message is not None
        assert message.find('Actual webelement:') == -1

    def test_collection_enabled_logging(self):

        browser.config.log_outer_html = True
        browser.open('http://todomvc.com/examples/emberjs/')

        message = None
        try:
            browser.all('footer p').element_by(have.attribute('wrong_attr')).should(be.visible)
        except Exception as e:
            message = str(e)

        assert message is not None
        assert message.find('Actual webelements collection:') != -1

    def test_collection_disabled_logging(self):

        browser.config.log_outer_html = False
        browser.open('http://todomvc.com/examples/emberjs/')

        message = None
        try:
            browser.all('footer p').element_by(have.attribute('wrong_attr')).should(be.visible)
        except Exception as e:
            message = str(e)

        assert message is not None
        assert message.find('Actual webelements collection:') == -1
