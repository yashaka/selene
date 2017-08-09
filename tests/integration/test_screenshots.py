import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from selene import config
from selene.conditions import exact_text, visible
from selene.browser import open_url, take_screenshot, set_driver, driver, latest_screenshot
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'
original_default_screenshot_folder = config.reports_folder
origina_timeout = config.timeout


def setup_function(f):
    config.reports_folder = original_default_screenshot_folder
    config.timeout = origina_timeout


def setup_module(m):
    set_driver(webdriver.Chrome(executable_path=ChromeDriverManager().install()))


def teardown_module(m):
    driver().quit()


def get_default_screenshot_folder():
    return config.reports_folder


def get_screen_id():
    return next(config.counter) - 1


def test_can_make_screenshot_with_default_name():
    open_url(start_page)
    actual = take_screenshot()

    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.exists(actual)


def test_can_make_screenshot_with_custom_name():
    open_url(start_page)
    actual = take_screenshot(filename="custom")

    expected = os.path.join(get_default_screenshot_folder(), 'custom.png')
    assert expected == actual
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_through_config():
    config.reports_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    open_url(start_page)
    actual = take_screenshot()

    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_as_parameter():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    open_url(start_page)
    actual = take_screenshot(path=screenshot_folder)

    expected = os.path.join(screenshot_folder,
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_with_custom_name():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    open_url(start_page)
    actual = take_screenshot(path=screenshot_folder,
                             filename="custom_file_in_custom_folder")

    expected = os.path.join(screenshot_folder, 'custom_file_in_custom_folder.png')
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_make_screenshot_automatically():
    open_url(start_page)
    config.timeout = 0.1
    with pytest.raises(TimeoutException) as ex:
        s("#selene_link").should_have(exact_text("Selen site"))
    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert os.path.exists(expected)


def test_can_get_latest_screenshot_path():
    config.reports_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    open_url(start_page)
    with pytest.raises(TimeoutException):
        s("#s").should_be(visible)

    picture = latest_screenshot
    assert os.path.exists(picture)