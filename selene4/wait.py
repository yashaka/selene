from selene4 import config

__author__ = 'ayia'

import time
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.common.exceptions import TimeoutException


def wait_for(entity, method, message='', timeout=config.timeout):
    """Calls the method provided with the driver as an argument until the \
    return value is not False."""
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
    raise TimeoutException(message, screen, stacktrace)


def has(entity, method):
    try:
        value = method(entity);
        return value if value is not None else False
    except (WebDriverException,) as exc:
        return False
