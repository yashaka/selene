import pytest

from selene.browser import driver, set_driver
from tests.acceptance.helpers.helper import get_test_driver


@pytest.fixture(scope='class')
def setup(request):
    set_driver(get_test_driver())

    def teardown():
        driver().quit()

    request.addfinalizer(teardown)


@pytest.mark.usefixtures("setup")
class BaseTest(object):
    pass
