import pytest

from selene.support import shared


def pytest_addoption(parser):

    parser.addoption(
        '--headless',
        help='headless mode',
        default=False,
    )


@pytest.fixture(scope='function')
def quit_shared_browser_afterwards():
    shared.browser.config.driver = ...

    yield

    shared.browser.quit()
