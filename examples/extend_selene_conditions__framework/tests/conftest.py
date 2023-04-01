import pytest

from selene.support.shared import browser


@pytest.fixture(scope='function', autouse=True)
def manage_browser():
    browser.config.base_url = 'https://demoqa.com'

    yield

    ...
