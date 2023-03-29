from dataclasses import fields

import pytest
import atexit

from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import MaxRetryError

import selene
from selene import browser
from selene.common.data_structures import persistent
from tests import resources

empty_page = resources.url('empty.html')


@pytest.fixture(scope='module')
def with_managed_browser_defaults_after_test_module():
    ...

    yield

    browser.quit()
    browser.config.driver = ...

    # reset all config fields to their default values
    for field in fields(selene.managed.Config):
        if not field.name.startswith('_') and field.name not in ['driver']:
            setattr(
                browser.config,
                field.name,
                getattr(selene.managed.Config(), field.name),
            )


@pytest.fixture(scope='function')
def given_reset_managed_browser_driver(
    with_managed_browser_defaults_after_test_module,
):
    browser.quit()
    browser.config.driver = ...

    yield

    ...


def test_can_init_default_chrome_browser_on_quit_o_o(
    # given_reset_managed_browser_driver,
):
    # GIVEN
    """
    Nothing ;)
    – this is a first test without any fixture in this module,
    so browser is not initialized yet.
    (TODO: improve this setup to be dead proof «not initialized yet»)
    """

    # WHEN we are going to do a stupid thing – quit non initialized browser yet
    browser.quit()

    # THEN we successfully quit it,
    #      as it was forced to initialize on request to driver under the hood
    webdriver: WebDriver = persistent.Field.value_from(
        browser.config, 'driver'
    )
    # AND exactly chrome was initialized
    assert webdriver.name == 'chrome'
    # AND now it is dead:
    pytest.raises(MaxRetryError, lambda: webdriver.title)
    # AND getting driver via public access also returns dead driver
    pytest.raises(MaxRetryError, lambda: browser.driver.title)


def test_can_init_default_chrome_browser_on_open(
    # given_reset_managed_browser_driver,
):
    # WHEN
    browser.open(empty_page)

    assert browser.driver.name == 'chrome'
    # browser.should(have.name('chrome'))  # TODO: do we need it?

    assert browser.driver.title == 'Selene Test Page'
    # browser.should(have.title('Selene Test Page'))


def test_browser_is_opened__on_access_to__browser_driver(
    # given_reset_managed_browser_driver,
):
    assert getattr(browser.config, '__boxed_driver').value is ...

    webdriver = browser.driver

    # TODO: consider checking actual process running (via psutil lib)
    assert getattr(browser.config, '__boxed_driver').value is webdriver
    assert webdriver.title == ''
    assert webdriver.name == 'chrome'


def test_browser_is_opened__on_access_to__browser_config_driver(
    given_reset_managed_browser_driver,
):
    assert getattr(browser.config, '_driver') is ...

    webdriver = browser.config.driver

    # TODO: consider checking actual process running (via psutil lib)
    assert getattr(browser.config, '_driver') is webdriver
    assert webdriver.title == ''
    assert webdriver.name == 'chrome'


def test_can_reset_driver_on_assigning_ellipsis(
    given_reset_managed_browser_driver,
):
    # GIVEN
    browser.open(empty_page)
    assert browser.driver.name == 'chrome'
    assert browser.driver.title == 'Selene Test Page'
    original_driver = browser.driver
    original_session_id = browser.driver.session_id

    # WHEN
    browser.config.driver = ...

    # THEN
    try:
        original_title = original_driver.title
        pytest.fail(
            f'should not be able to get title {original_title} from closed driver'
        )
    except Exception as error:
        '''
        original browser is dead;)
        '''
        assert 'Failed to establish a new connection' in str(error)

    # WHEN
    browser.open(empty_page)

    # THEN
    assert browser.driver.name == 'chrome'
    assert browser.driver.title == 'Selene Test Page'
    assert original_session_id != browser.driver.session_id


def test_can_init_custom_firefox_browser_on_open(
    given_reset_managed_browser_driver,
):
    browser.config.browser_name = 'firefox'

    browser.open(empty_page)

    assert browser.driver.name == 'firefox'
    assert browser.driver.title == 'Selene Test Page'


def test_can_reset_custom_firefox_driver_on_assigning_ellipsis(
    given_reset_managed_browser_driver,
):
    # GIVEN
    browser.config.browser_name = 'firefox'
    browser.open(empty_page)
    original_driver = browser.driver
    original_session_id = browser.driver.session_id

    # WHEN
    browser.config.driver = ...

    # THEN
    try:
        original_title = original_driver.title
        pytest.fail(
            f'should not be able to get title {original_title} from closed driver'
        )
    except Exception as error:
        '''
        original browser is dead;)
        '''
        assert 'Failed to establish a new connection' in str(error)

    # WHEN
    browser.open(empty_page)

    # THEN
    assert browser.driver.name == 'firefox'
    assert original_session_id != browser.driver.session_id


def test_can_init_another_browser_after_custom_only_after_custom_browser_quit(
    given_reset_managed_browser_driver,
):
    # AND
    browser.config.browser_name = 'firefox'
    browser.open(empty_page)
    assert browser.driver.name == 'firefox'
    firefox_session_id = browser.driver.session_id

    # WHEN
    browser.config.browser_name = 'chrome'

    # THEN still the same firefox session
    # TODO: should we change this behavior? see https://github.com/yashaka/selene/issues/453
    assert browser.driver.name == 'firefox'
    assert browser.driver.session_id == firefox_session_id

    # WHEN
    browser.open(empty_page)

    # THEN still the same firefox session
    assert browser.driver.name == 'firefox'
    assert browser.driver.session_id == firefox_session_id

    # WHEN
    browser.quit()
    # AND
    browser.open(empty_page)

    # THEN finally new chrome session
    assert browser.driver.name == 'chrome'
    assert browser.driver.session_id != firefox_session_id


def test_browser_is_closed_on_exit_by_default_false_in_hold_browser_open(
    given_reset_managed_browser_driver,
):
    original_driver = browser.driver

    atexit._run_exitfuncs()  # noqa

    try:
        original_title = original_driver.title
        pytest.fail(
            f'should not be able to get title {original_title} from closed driver'
        )
    except Exception as error:
        '''
        original browser is dead;)
        '''
        assert 'Failed to establish a new connection' in str(error)


def test_hold_browser_open_on_explicit_true__set_before_browser_is_opened(
    given_reset_managed_browser_driver,
):
    browser.config.hold_browser_open = True
    original_driver = browser.driver

    atexit._run_exitfuncs()  # noqa

    # THEN driver is still alive
    assert original_driver.title == ''


def test_hold_browser_open_on_explicit_true__set_after_browser_is_opened(
    given_reset_managed_browser_driver,
):
    original_driver = browser.driver

    browser.config.hold_browser_open = True
    atexit._run_exitfuncs()  # noqa

    # THEN driver is still alive
    assert original_driver.title == ''
