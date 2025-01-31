import pytest

from examples.run_cross_platform_android_ios import project
from examples.run_cross_platform_android_ios.wikipedia_app_tests import support
from selene.support._mobile import device


@pytest.fixture(scope='function', autouse=True)
def driver_management():
    device.config.driver_options = project.config.to_driver_options()
    device.config.driver_remote_url = project.config.driver_remote_url
    device.config.selector_to_by_strategy = support.mobile_selectors.to_by_strategy
    device.config.timeout = 8.0

    yield

    device.driver.quit()
