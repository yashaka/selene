import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from selene import config
from selene.conditions import exact_text, visible
from selene.tools import visit, take_screenshot, s, set_driver, get_driver, get_latest_screenshot

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'
original_default_screenshot_folder = config.screenshot_folder
origina_timeout = config.timeout


def setup_function(f):
    config.screenshot_folder = original_default_screenshot_folder
    config.timeout = origina_timeout


def setup_module(m):
    set_driver(webdriver.Chrome(executable_path=ChromeDriverManager().install()))


def teardown_module(m):
    get_driver().quit()


def get_default_screenshot_folder():
    return config.screenshot_folder


def get_screen_id():
    return next(config.counter) - 1


def test_can_make_screenshot_with_default_name():
    visit(start_page)
    actual = take_screenshot()

    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.exists(actual)


def test_can_make_screenshot_with_custom_name():
    visit(start_page)
    actual = take_screenshot(filename="custom")

    expected = os.path.join(get_default_screenshot_folder(), 'custom.png')
    assert expected == actual
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_through_config():
    config.screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot()

    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_as_parameter():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot(path=screenshot_folder)

    expected = os.path.join(screenshot_folder,
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_with_custom_name():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot(path=screenshot_folder,
                             filename="custom_file_in_custom_folder")

    expected = os.path.join(screenshot_folder, 'custom_file_in_custom_folder.png')
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_make_screenshot_automatically():
    visit(start_page)
    config.timeout = 0.1
    with pytest.raises(TimeoutException) as ex:
        s("#selene_link").should_have(exact_text("Selen site"))
    expected = os.path.join(get_default_screenshot_folder(),
                            'screen_{id}.png'.format(id=get_screen_id()))
    assert os.path.exists(expected)


def test_can_get_latest_screenshot_path():
    config.screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    with pytest.raises(TimeoutException):
        s("#s").should_be(visible)

    picture = get_latest_screenshot()
    assert os.path.exists(picture)