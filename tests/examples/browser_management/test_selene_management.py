from dataclasses import fields

import pytest
import atexit

from selenium.webdriver.remote.webdriver import WebDriver
from urllib3.exceptions import MaxRetryError

import selene
from selene import browser, have
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


def test_new_config_does_not_build_driver_on_init():

    # WHEN
    config = selene.Config()

    driver = persistent.Field.value_from(config, 'driver')
    assert driver is ...


def test_first_access_to_driver_on_config_ensures_driver_for_chrome_is_built():

    # WHEN
    config = selene.Config()

    driver = config.driver
    assert driver.name == 'chrome'
    assert driver.title == ''


def test_automatically_built_driver_is_stored_as_persistent_value_in_config():
    config = selene.Config()

    driver = config.driver

    assert driver is persistent.Field.value_from(config, 'driver')


def test_persistent_means___():
    """
    TBD
    """


def test_new_browser_does_not_build_driver_on_init():

    # WHEN
    browser = selene.Browser(selene.Config())

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver is ...


def test_first_access_to_driver_on_browser_ensures_driver_for_chrome_is_built():
    browser = selene.Browser(selene.Config())

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''
    driver = persistent.Field.value_from(browser.config, 'driver')


def test_first_access_to_driver_on_browser_config_ensures_driver_for_chrome_is_built():
    browser = selene.Browser(selene.Config())

    driver = browser.config.driver

    assert driver.name == 'chrome'
    assert driver.title == ''
    driver = persistent.Field.value_from(browser.config, 'driver')


def test_first_access_to_driver_via_browser_open__builds_driver():
    browser = selene.Browser(selene.Config())

    browser.open(empty_page)

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.name == 'chrome'
    assert driver.title == 'Selene Test Page'


def test_built_driver_will_be_killed_on_process_exit():
    browser = selene.Browser(selene.Config())
    browser.open(empty_page)

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    pytest.raises(MaxRetryError, lambda: driver.title)  # KILLED


def test_built_driver_will_not_be_killed_if_configured_with_hold_driver():
    browser = selene.Browser(
        selene.Config(
            hold_driver_at_exit=True,  # <- GIVEN
        )
    )
    browser.open(empty_page)

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_built_driver_will_not_be_killed_if_post_configured_for_hold_driver():
    browser = selene.Browser(selene.Config())
    browser.open(empty_page)
    browser.config.hold_driver_at_exit = True  # <- GIVEN

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_built_on_clone_driver_will_not_be_killed_if_cloned_with_hold_driver():
    browser = selene.Browser(selene.Config())
    clone = browser.with_(hold_driver_at_exit=True)  # <- GIVEN
    clone.open(empty_page)  # <- AND

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(clone.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_built_on_browser_driver_will_be_killed_even_if_cloned_with_hold_driver():
    browser = selene.Browser(selene.Config())
    clone = browser.with_(hold_driver_at_exit=True)  # <- GIVEN
    browser.open(empty_page)  # <- AND

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    pytest.raises(MaxRetryError, lambda: driver.title)  # KILLED


def test_first_access_to_driver_via_browser_quit__builds_and_kills_driver():
    browser = selene.Browser(selene.Config())

    # WHEN we are going to do a stupid thing – quit non initialized browser yet
    browser.quit()

    # THEN we successfully quit it,
    #      as it was forced to initialize on request to driver under the hood
    driver = persistent.Field.value_from(browser.config, 'driver')
    # AND now it is dead:
    pytest.raises(MaxRetryError, lambda: driver.title)
    # AND getting driver via public access on browser
    #     with explicit ask to not rebuild driver
    #     will also return dead driver:
    pytest.raises(
        MaxRetryError,
        lambda: browser.with_(rebuild_dead_driver=False).driver.title,
    )


def test_can_rebuild_browser_on_first_access_after_its_death():
    browser = selene.Browser(selene.Config())
    browser.quit()

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''  # alive;)
    assert driver is persistent.Field.value_from(browser.config, 'driver')


def test_browser_remains_dead_if_configured_with_not_rebuild_dead_driver_on_init():

    browser = selene.Browser(
        selene.Config(
            rebuild_dead_driver=False,  # <- WHEN
        )
    )
    browser.quit()
    driver = browser.driver

    assert driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: driver.title)  # THEN yet dead


def test_browser_remains_dead_if_post_configured_for_not_rebuild_dead_driver():
    browser = selene.Browser(selene.Config())
    browser.quit()

    browser.config.rebuild_dead_driver = False  # <- WHEN
    driver = browser.driver

    assert driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: driver.title)  # THEN yet dead


def test_browser_clone_remains_dead_if_cloned_with_not_rebuild_dead_driver():
    browser = selene.Browser(selene.Config())
    browser.quit()

    clone = browser.with_(rebuild_dead_driver=False)  # <- WHEN

    assert clone.driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: clone.driver.title)  # THEN yet dead


def test_browser_resurrects_itself_and_clone_after_clone_programmed_to_death_forever():
    browser = selene.Browser(selene.Config())
    browser.quit()
    clone = browser.with_(rebuild_dead_driver=False)  # <- GIVEN

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''  # alive;)
    assert driver is persistent.Field.value_from(browser.config, 'driver')
    assert driver is clone.driver
    assert driver is persistent.Field.value_from(clone.config, 'driver')


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


"""
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
    
"""
