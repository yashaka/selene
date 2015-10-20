from selene4 import config

__author__ = 'ayia'

import time
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.common.exceptions import TimeoutException


def wait_for(entity, method, message=''):
    """Calls the method provided with the driver as an argument until the \
    return value is not False."""
    screen = None
    stacktrace = None

    end_time = time.time() + config.timeout
    while True:
        try:
            value = method(entity)
            if value is not (None or False):
                return value
        except (WebDriverException,) as exc:
            screen = getattr(exc, 'screen', None)
            stacktrace = getattr(exc, 'stacktrace', None)
        time.sleep(config.poll_during_waits)
        if time.time() > end_time:
            break
    raise TimeoutException(message, screen, stacktrace)