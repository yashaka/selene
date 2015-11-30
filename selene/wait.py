from selene import config

__author__ = 'ayia'

import time
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.common.exceptions import TimeoutException


def wait_for(entity, method, message='', timeout=None):
    if not timeout:
        timeout = config.timeout
    screen = None
    stacktrace = None

    end_time = time.time() + timeout
    while True:
        try:
            value = method(entity)
            if value is not None:
                return value
        except (WebDriverException,) as exc:
            screen = getattr(exc, 'screen', None)
            stacktrace = getattr(exc, 'stacktrace', None)
        time.sleep(config.poll_during_waits)
        if time.time() > end_time:
            break
    raise TimeoutException(
        """
            failed while waiting %s seconds
            to assert %s%s
        """ % (timeout, method.__class__.__name__, message), screen, stacktrace)


def wait_for_not(entity, method, message='', timeout=None):
    if not timeout:
        timeout = config.timeout
    end_time = time.time() + timeout
    while True:
        try:
            value = method(entity)
            if value is None:
                return value
        except (WebDriverException,) as exc:
            return True
        time.sleep(config.poll_during_waits)
        if time.time() > end_time:
            break
    raise TimeoutException(
        """
            failed while waiting %s seconds
            to assert not %s%s
        """ % (timeout, method.__class__.__name__, message))


def has(entity, method):
    try:
        value = method(entity);
        return value if value is not None else False
    except (WebDriverException,) as exc:
        return False

def has_not(entity, method):
    try:
        value = method(entity);
        return value if value is None else True
    except (WebDriverException,) as exc:
        return True
