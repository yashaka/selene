import atexit
import pytest

from urllib3.exceptions import MaxRetryError  # type: ignore

import selene
from selene.common.data_structures import persistent
from tests import resources

empty_page = resources.url('empty.html')


@pytest.fixture(scope='function')
def with_process_exit_teardown():
    # ...

    yield

    atexit._run_exitfuncs()


@pytest.fixture(scope='function')
def manual_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service  # type: ignore
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
    from webdriver_manager.core.utils import ChromeType

    manual_driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        )
    )

    yield manual_driver

    if (
        manual_driver.service.process is not None
        and manual_driver.service.process.poll() is None
    ):
        manual_driver.quit()


@pytest.fixture(scope='function')
def a_browser_built_with__override_driver_with_all_driver_like_options__disabled():
    yield selene.Browser(
        selene.Config(_override_driver_with_all_driver_like_options=False)
    )


def test_new_config_does_not_build_driver_on_init(with_process_exit_teardown):
    # WHEN
    config = selene.Config()

    driver = persistent.Field.value_from(config, 'driver')
    assert driver is ...


def test_first_access_to_driver_on_config_ensures_driver_for_chrome_is_built(
    with_process_exit_teardown,
):
    # WHEN
    config = selene.Config()

    driver = config.driver
    assert driver.name == 'chrome'
    assert driver.title == ''


def test_automatically_built_driver_is_stored_as_persistent_value_in_config(
    with_process_exit_teardown,
):
    config = selene.Config()

    driver = config.driver

    assert driver is persistent.Field.value_from(config, 'driver')


def test_persistent_means___(with_process_exit_teardown):
    """
    TBD
    """


def test_new_browser_does_not_build_driver_on_init(with_process_exit_teardown):
    # WHEN
    browser = selene.Browser(selene.Config())

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver is ...


def test_first_access_to_driver_on_browser_ensures_driver_for_chrome_is_built(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''
    driver = persistent.Field.value_from(browser.config, 'driver')


def test_first_access_to_driver_on_browser_config_ensures_driver_for_chrome_is_built(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())

    driver = browser.config.driver

    assert driver.name == 'chrome'
    assert driver.title == ''
    driver = persistent.Field.value_from(browser.config, 'driver')


def test_first_access_to_driver_via_browser_open__builds_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())

    browser.open(empty_page)

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.name == 'chrome'
    assert driver.title == 'Selene Test Page'


def test_built_driver_will_be_killed_on_process_exit(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    browser.open(empty_page)

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    pytest.raises(MaxRetryError, lambda: driver.title)  # KILLED


def test_built_driver_will_not_be_killed_if_configured_with_hold_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(
        selene.Config(
            hold_driver_at_exit=True,  # <- GIVEN
        )
    )
    browser.open(empty_page)

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_built_driver_will_not_be_killed_if_post_configured_for_hold_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    browser.open(empty_page)
    browser.config.hold_driver_at_exit = True  # <- GIVEN

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_driver_built_on_copy__will_not_be_killed__if_copied_with_hold_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    copied = browser.with_(hold_driver_at_exit=True)  # <- GIVEN
    copied.open(empty_page)  # <- AND

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(copied.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_driver_built_on_copy__will_not_be_killed__if_copied_with_hold_driver_if(
    a_browser_built_with__override_driver_with_all_driver_like_options__disabled,
    with_process_exit_teardown,
):
    browser = a_browser_built_with__override_driver_with_all_driver_like_options__disabled
    copied = browser.with_(hold_driver_at_exit=True)  # <- GIVEN
    copied.open(empty_page)  # <- AND

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(copied.config, 'driver')
    assert driver.title == 'Selene Test Page'  # ALIVE


def test_driver_built_on_browser__will_be_killed_even__if_copied_with_hold_driver_if(
    a_browser_built_with__override_driver_with_all_driver_like_options__disabled,
    with_process_exit_teardown,
):
    browser = a_browser_built_with__override_driver_with_all_driver_like_options__disabled
    copied = browser.with_(hold_driver_at_exit=True)  # <- GIVEN
    browser.open(empty_page)  # <- AND

    atexit._run_exitfuncs()

    driver = persistent.Field.value_from(browser.config, 'driver')
    pytest.raises(MaxRetryError, lambda: driver.title)  # KILLED


def test_first_access_to_driver_via_browser_quit__builds_and_kills_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config(rebuild_dead_driver=False))

    # WHEN we are going to do a stupid thing – quit non initialized browser yet
    browser.quit()

    # THEN we successfully quit it,
    #      as it was forced to initialize on request to driver under the hood
    driver = persistent.Field.value_from(browser.config, 'driver')
    # AND now it is dead:
    pytest.raises(MaxRetryError, lambda: driver.title)
    # AND getting driver via public access on browser
    #     will also return dead driver:
    #     GIVEN previously built browser with Config(rebuild_dead_driver=False)
    pytest.raises(MaxRetryError, lambda: browser.driver.title)


def test_can_rebuild_browser_on_first_access_after_its_death(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    browser.quit()

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''  # alive;)
    assert driver is persistent.Field.value_from(browser.config, 'driver')


def test_browser_remains_dead_if_configured_with_not_rebuild_dead_driver_on_init(
    with_process_exit_teardown,
):
    browser = selene.Browser(
        selene.Config(
            rebuild_dead_driver=False,  # <- WHEN
        )
    )
    browser.quit()
    driver = browser.driver

    assert driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: driver.title)  # THEN yet dead


def test_browser_remains_dead_if_post_configured_for_not_rebuild_dead_driver(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    browser.quit()

    browser.config.rebuild_dead_driver = False  # <- WHEN
    driver = browser.driver

    assert driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: driver.title)  # THEN yet dead


def test_browser_copy_remains_dead__if_copied_with_not_rebuild_dead_driver_if(
    a_browser_built_with__override_driver_with_all_driver_like_options__disabled,
    with_process_exit_teardown,
):
    browser = a_browser_built_with__override_driver_with_all_driver_like_options__disabled
    browser.quit()

    copy = browser.with_(rebuild_dead_driver=False)  # <- WHEN

    assert copy.driver.name == 'chrome'
    pytest.raises(MaxRetryError, lambda: copy.driver.title)  # THEN yet dead


def test_browser_resurrects_itself_and_copy__after_copy_programmed_to_death_forever_if(
    a_browser_built_with__override_driver_with_all_driver_like_options__disabled,
    with_process_exit_teardown,
):
    browser = a_browser_built_with__override_driver_with_all_driver_like_options__disabled
    browser.quit()
    copy = browser.with_(rebuild_dead_driver=False)  # <- GIVEN

    driver = browser.driver

    assert driver.name == 'chrome'
    assert driver.title == ''  # alive;)
    assert driver is persistent.Field.value_from(browser.config, 'driver')
    assert driver is copy.driver
    assert driver is persistent.Field.value_from(copy.config, 'driver')


def test_can_build_second_driver_if_previous_was_forgotten(
    with_process_exit_teardown,
):
    # GIVEN
    browser = selene.Browser(selene.Config())
    first_driver = browser.driver

    # WHEN
    browser.config.driver = ...

    # THEN
    assert first_driver.title == ''  # ALIVE;)

    # WHEN
    second_driver = browser.driver

    # THEN
    assert second_driver.title == ''  # NEW ONE!
    assert first_driver.title == ''  # OLD IS ALIVE;)
    assert first_driver.session_id != second_driver.session_id


def test_should_kill_at_exit_all_built_drivers_including_forgotten_for_same_browser(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    first_driver = browser.driver
    browser.config.driver = ...
    second_driver = browser.driver

    atexit._run_exitfuncs()

    pytest.raises(MaxRetryError, lambda: first_driver.title)  # KILLED
    pytest.raises(MaxRetryError, lambda: second_driver.title)  # KILLED


def test_driver_can_be_manually_set_on_init_and_live_to_death_on_quit(
    with_process_exit_teardown, manual_driver
):
    # WHEN
    browser = selene.Browser(selene.Config(driver=manual_driver))

    assert manual_driver is browser.driver

    # WHEN
    browser.open(empty_page)

    assert browser.driver.title == 'Selene Test Page'  # ALIVE
    assert manual_driver is browser.driver

    # WHEN
    browser.quit()

    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # DEAD
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_driver_can_be_manually_post_set_and_live_to_death_on_quit(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(selene.Config())

    # WHEN
    browser.config.driver = manual_driver

    assert manual_driver is browser.driver

    # WHEN
    browser.open(empty_page)

    assert browser.driver.title == 'Selene Test Page'  # ALIVE
    assert manual_driver is browser.driver

    # WHEN
    browser.quit()

    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # DEAD
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_set_on_init_and_used_manual_driver_should_be_killed_by_default(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(
        selene.Config(
            driver=manual_driver,  # <- GIVEN
        )
    )
    browser.open(empty_page)  # <- AND

    # WHEN
    atexit._run_exitfuncs()

    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # DEAD


def test_set_on_init_and_not_used_manual_driver_should_not_be_killed_if_post_configured_to_hold(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(
        selene.Config(
            driver=manual_driver,  # <- GIVEN
        )
    )
    browser.config.hold_driver_at_exit = True  # <- AND
    # browser.open(empty_page)  # <- AND not used

    # WHEN
    atexit._run_exitfuncs()

    assert manual_driver.title == ''  # ALIVE
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_post_set_and_used_manual_driver_should_not_be_killed_if_pre_configured_to_hold(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(
        selene.Config(
            hold_driver_at_exit=True,  # <- GIVEN
        )
    )
    browser.config.driver = manual_driver
    browser.open(empty_page)  # <- AND

    # WHEN
    atexit._run_exitfuncs()

    assert manual_driver.title == 'Selene Test Page'  # ALIVE
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_post_set_and_used_manual_driver_should_be_killed_by_default(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(selene.Config())
    browser.config.driver = manual_driver  # <- GIVEN
    browser.open(empty_page)  # <- AND

    # WHEN
    atexit._run_exitfuncs()

    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # DEAD
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_post_set_not_used_manual_driver_should_be_killed_by_default(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(selene.Config())
    browser.config.driver = manual_driver  # <- GIVEN
    # browser.open(empty_page)  # <- AND not used

    # WHEN
    atexit._run_exitfuncs()

    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # DEAD
    assert manual_driver is persistent.Field.value_from(
        browser.config, 'driver'
    )


def test_can_build_second_driver_if_first_manually_set_on_init_was_used_n_forgotten(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(selene.Config())
    browser.config.driver = manual_driver
    browser.open(empty_page)

    # WHEN
    browser.config.driver = ...

    # THEN
    assert manual_driver.title == 'Selene Test Page'  # ALIVE;)

    # WHEN
    second_driver = browser.driver

    # THEN
    assert second_driver.title == ''  # NEW ONE!
    assert manual_driver.title == 'Selene Test Page'  # OLD IS ALIVE;)
    assert manual_driver.session_id != second_driver.session_id


def test_should_kill_at_exit_all_drivers_including_manually_set_n_forgotten(
    with_process_exit_teardown, manual_driver
):
    browser = selene.Browser(selene.Config())
    first_driver = browser.driver
    browser.config.driver = manual_driver
    browser.config.driver = (
        manual_driver  # just in case:) TODO: move to separate test
    )
    browser.config.driver = ...
    third_driver = browser.driver

    # WHEN
    atexit._run_exitfuncs()

    pytest.raises(MaxRetryError, lambda: first_driver.title)  # KILLED
    pytest.raises(MaxRetryError, lambda: manual_driver.title)  # KILLED
    pytest.raises(MaxRetryError, lambda: third_driver.title)  # KILLED


def test_builds_firefox_driver_for_browser_configured_with_firefox_as_name(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config(driver_name='firefox'))

    driver = browser.driver

    assert driver.name == 'firefox'
    assert driver.title == ''


def test_builds_firefox_driver_for_browser_post_tuned_for_firefox_as_name(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    browser.config.driver_name = 'firefox'

    driver = browser.driver

    assert driver.name == 'firefox'
    assert driver.title == ''


def test_proceed_with_built_before_driver_if_post_tuned_after_driver_access(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    driver = browser.driver

    browser.config.driver_name = 'firefox'

    assert browser.driver.name == 'chrome'
    assert browser.driver.title == ''
    assert driver is browser.driver


def test_build_post_tuned_driver_by_name_on_second_access_after_first_quit(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    driver = browser.driver
    browser.config.driver_name = 'firefox'

    browser.quit()
    driver = browser.driver

    assert driver.name == 'firefox'
    assert driver.title == ''


def test_build_post_tuned_driver_by_name_on_second_access_after_first_reset(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())
    driver = browser.driver
    browser.config.driver_name = 'firefox'

    browser.config.driver = ...
    driver = browser.driver

    assert driver.name == 'firefox'
    assert driver.title == ''


def test_builds_firefox_driver_when_accessed_via_inline_copy(
    with_process_exit_teardown,
):
    browser = selene.Browser(selene.Config())

    driver = browser.with_(driver_name='firefox').driver

    assert driver.name == 'firefox'
    assert driver.title == ''


def test_firefox_built_via_copy_is_kept_for_original_browser__if_preconfigured(
    with_process_exit_teardown,
):
    browser = selene.Browser(
        selene.Config(
            _override_driver_with_all_driver_like_options=False
        )  # <- GIVEN
    )

    copy = browser.with_(driver_name='firefox')
    driver_of_copy = copy.driver
    browser.open(empty_page)

    assert driver_of_copy is browser.driver
    assert browser.driver.name == 'firefox'


def test_post_configured_sharing_driver_between_original_and_copy_when_only_name_differs(
    with_process_exit_teardown,
):
    origin = selene.Browser(selene.Config())
    '''
    # same as:
    origin = selene.Browser(selene.Config(driver_name='chrome'))
    '''
    origin.config._override_driver_with_all_driver_like_options = (
        False  # <- GIVEN
    )
    copied = origin.with_(driver_name='firefox')  # <- AND

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is driver_of_origin


def test_preconfigured_sharing_driver_between_original_and_copy_when_nothing_differs(
    with_process_exit_teardown,
):
    origin = selene.Browser(
        selene.Config(
            _override_driver_with_all_driver_like_options=False,  # <- GIVEN
        )
    )
    copied = origin.with_()  # <- AND nothing

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is driver_of_origin


def test_preconfigured_new_driver_for_copy_by_explicit_driver_set_on_cloning_nothing(
    with_process_exit_teardown,
):
    origin = selene.Browser(
        selene.Config(
            _override_driver_with_all_driver_like_options=False,  # <- GIVEN
        )
    )
    copied = origin.with_(driver=...)  # <- AND

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is not driver_of_origin


def test_new_driver_for_copy_by_explicit_driver_set_on_cloning_nothing(
    with_process_exit_teardown,
):
    origin = selene.Browser(selene.Config())  # <- GIVEN
    copied = origin.with_(driver=...)  # <- AND

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is not driver_of_origin


def test_post_configured_new_driver_for_copy_by_explicit_driver_set_on_cloning_with_name(
    with_process_exit_teardown,
):
    origin = selene.Browser(selene.Config())
    origin.config._override_driver_with_all_driver_like_options = (
        False  # <- GIVEN
    )
    copied = origin.with_(driver_name='firefox', driver=...)  # <- AND

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is not driver_of_origin


def test_new_driver_for_copy_by_implicit_driver_set_on_cloning_with_name(
    with_process_exit_teardown,
):
    origin = selene.Browser(selene.Config())
    '''
    # because of default behavior, is same as:
    origin = selene.Browser(
        selene.Config(_override_driver_with_all_driver_like_options=True)
    )
    '''
    copied = origin.with_(driver_name='firefox')  # <- AND

    driver_of_copied = copied.driver
    driver_of_origin = origin.driver

    assert driver_of_copied is not driver_of_origin
