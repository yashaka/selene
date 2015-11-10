import pytest

from selene import settings, s
from selene.waits import wait_for, ExpiredWaitingException


def setup_module():
    settings.default_wait_time = 0.1


def test_wait_for_without_conditions():
    text = 'Text'
    assert wait_for(lambda: text, None) is text


def test_wait_for_with_correct_conditions():
    text = 'Text'
    assert wait_for(lambda: text, lambda r: len(r) > 0) is text


def test_wait_for_with_incorrect_conditions():
    with pytest.raises(ExpiredWaitingException):
        wait_for(lambda: 'text', lambda r: len(r) == 0)


def test_wait_for_with_by_demand_after():
    class Error(Exception):
        pass

    def demand():
        raise Error()

    with pytest.raises(Error):
        wait_for(lambda: 'text', lambda r: len(r) == 0, demand)


def test_wait_for_with_passed_waiting():
    class Code(object):
        def __init__(self):
            self._number = 1

        def plus_one(self):
            self._number += 1
            return self._number

    c = Code()
    assert wait_for(lambda: c.plus_one(), lambda r: r == 25, wait_time=4) == 25


def test_wait_for_element_which_does_not_exist():
    with pytest.raises(ExpiredWaitingException):
        s("#i-do-not-exist").insist()


def test_wait_for_element_with_off_screenshoting():
    try:
        settings.screenshot_on_element_fail = False
        s("#i-do-not-exist").insist()
        assert "ExpiredWaitingException must be"
    except ExpiredWaitingException as e:
        assert 'settings.screenshot_on_element_fail = False' in e.message
    finally:
        settings.screenshot_on_element_fail = True
