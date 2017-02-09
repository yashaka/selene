import atexit

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

import selene
from selene import config
from selene.browsers import Browser


def set_shared_driver(driver):
    selene.driver._shared_web_driver_source.driver = driver
    config.browser_name = driver.name


def get_shared_driver():
    return selene.driver._shared_web_driver_source.driver


def is_another_driver(driver):
    try:
        return get_shared_driver().session_id != driver.session_id
    except AttributeError:
        return False


def is_driver_still_open(driver):
    # type: (WebDriver) -> bool
    try:
        driver.title
    # todo: specify exception?.. (unfortunately there Selenium does not use some specific exception for this...)
    except Exception:
        return False
    return True


def driver_has_started(name):
    shared_driver = get_shared_driver()
    if not shared_driver:
        return False
    return shared_driver.name == name \
           and shared_driver.session_id \
           and is_driver_still_open(shared_driver)


def kill_all_started_drivers():
    atexit._run_exitfuncs()


def ensure_driver_started(name):
    if driver_has_started(name):
        return get_shared_driver()

    return _start_driver(name)


def __start_chrome():
    options = webdriver.ChromeOptions()
    if config.maximize_window:
        options.add_argument("--start-maximized")
    return webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                            chrome_options=options,
                            desired_capabilities=config.desired_capabilities)


def __start_firefox(name):
    executable_path = "wires"
    if name == Browser.MARIONETTE:
        executable_path = GeckoDriverManager().install()
    driver = webdriver.Firefox(capabilities=config.desired_capabilities,
                               executable_path=executable_path)
    if config.maximize_window:
        driver.maximize_window()
    return driver


def __get_driver(name):
    if name == Browser.CHROME:
        return __start_chrome()
    else:
        return __start_firefox(name)


def _start_driver(name):
    kill_all_started_drivers()
    driver = __get_driver(name)
    set_shared_driver(driver)
    if not config.hold_browser_open:
        _register_driver(driver)
    return driver


def _register_driver(driver):
    atexit.register(driver.quit)
