import pytest
from selenium import webdriver
import selene4


@pytest.fixture(scope='class')
def setup(request):
    # todo: refactor to: set_driver(webdriver.Firefox())
    selene4.config.driver = webdriver.Firefox()

    def teardown():
        # todo: refactor to: get_driver().quit()
        selene4.config.driver.quit()

    request.addfinalizer(teardown)


@pytest.mark.usefixtures("setup")
class BaseTest(object):
    pass
