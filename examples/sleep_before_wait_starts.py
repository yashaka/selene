import time
import pytest

from selene import browser
from selene.core.wait import Wait

DEFAULT_SLEEP_TIME = 1.0
CUSTOM_SLEEP_TIME = 5.0


def sleep_before_wait(wait: Wait, sleep_time=DEFAULT_SLEEP_TIME):
    def sleep_before_wait_decorator(for_):
        def decorated(fn):
            time.sleep(sleep_time)
            try:
                res = for_(fn)
                return res
            except Exception as error:
                raise error

        return decorated

    return sleep_before_wait_decorator


@pytest.fixture(scope='function')
def browser_management_with_default_sleep():
    browser.config._wait_decorator = sleep_before_wait

    yield


@pytest.fixture(scope='function')
def browser_management_with_custom_sleep():
    def custom_sleep_decorator(fn):
        return sleep_before_wait(fn, sleep_time=CUSTOM_SLEEP_TIME)

    browser.config._wait_decorator = custom_sleep_decorator

    yield


def test_sleep_via__wait_decorator(browser_management_with_default_sleep):
    """
    Waits 1 second each before typing and pressing enter
    So the difference between epoch time should be equal to or more that 2

    """
    browser.open('http://todomvc.com/examples/emberjs/')
    for _ in range(2):
        browser.element('#new-todo').type(f'{time.time()}').press_enter()
    todo_items = browser.all('#todo-list>li')
    initial_epoch_time = float(todo_items.first().text)
    final_epoch_time = float(todo_items.second().text)

    assert final_epoch_time - initial_epoch_time >= 2 * DEFAULT_SLEEP_TIME


def test_sleep_via_wait_decorator_with_custom_time(
    browser_management_with_custom_sleep,
):
    """
    Waits 0.5 second each before typing and pressing enter
    So the difference between epoch time should be equal to or more that 1

    """
    browser.open('http://todomvc.com/examples/emberjs/')
    for _ in range(2):
        browser.element('#new-todo').type(f'{time.time()}').press_enter()
    todo_items = browser.all('#todo-list>li').sliced(2)
    initial_epoch_time = float(todo_items.first().text)
    final_epoch_time = float(todo_items.second().text)

    assert final_epoch_time - initial_epoch_time >= 2 * CUSTOM_SLEEP_TIME
