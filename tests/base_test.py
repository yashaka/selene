import pytest
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

from selene.tools import get_driver, set_driver


@pytest.fixture(scope='class')
def setup(request):
    set_driver(webdriver.Firefox(executable_path=GeckoDriverManager().install()))

    def teardown():
        get_driver().quit()

    request.addfinalizer(teardown)


@pytest.mark.usefixtures("setup")
class BaseTest(object):
    pass
