import time
from httplib import CannotSendRequest

import stopit
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, WebDriverException

from selene import settings
from selene.condition_helpers import satisfied
from selene.driver import screenshot
from selene.helpers import suppress


class DummyResult(object):
    def __getattr__(self, item):
        return lambda *args, **kwargs: False


class ExpiredWaitingException(Exception):
    pass


def _time_finished_action():
    raise ExpiredWaitingException()


def wait_for(code, until, by_demand_after=None, wait_time=0.1, exceptions=None,
             expired_waiting_code=_time_finished_action):
    """
    Wait for a `wait_time` smartly for the `until` conditions to be satisfied on the result of executing `code`.
    But after the `after` code was executed optionally in case code() gave no satisfied result at first attempt.

    :param code: code (function) to be executed
    :param until: single condition or list (tuple) of conditions. For example: lambda result: result.is_displayed()
    :param by_demand_after:
    :param wait_time: a time to wait for the code
    :param exceptions:
    :param expired_waiting_code:
    :return: result of code() execution
    """
    # todo: think on: better name for by_demand_after, or even another way to implement this feature
    # todo: think on: letting the wait_for to accept hamcrest matchers as 'until' conditions

    conditions = until if isinstance(until, (tuple, list)) else [until] if until else []

    result = DummyResult()
    with suppress(exceptions):
        result = code()

    if len(conditions) > 0 and not satisfied(result, *conditions):
        if by_demand_after:
            by_demand_after()
    else:
        return result

    with stopit.ThreadingTimeout(wait_time):
        while True:
            with suppress(exceptions):
                time.sleep(0.1)
                result = code()
                if satisfied(result, *conditions):
                    return result
    expired_waiting_code()
    return result


def wait_for_element(element_finder, until=lambda code_result: False, by_demand_after=lambda: None,
                     wait_time=settings.time_of_element_appearence):
    exceptions = (StaleElementReferenceException, NoSuchElementException, CannotSendRequest)

    def as_str(item):
        if isinstance(item, (tuple, list)):
            s = ''
            for item in item:
                if s:
                    s += ' and '
                s += item.__name__  # todo: think on: refactoring to the usage without "underscores"
            return s
        return item.__name__

    def final_code():
        err_message = """
        Timeout reached while waiting...
        During: %ss
        For: %s
        Until: %s
        Screenshot: %s
        """ % (wait_time,
               as_str(element_finder),
               as_str(until),
               "Disabled: selene.settings.screenshot_on_element_fail = False" \
                                         if not settings.screenshot_on_element_fail else screenshot())
        raise ExpiredWaitingException(err_message)

    return wait_for(element_finder, until, by_demand_after, wait_time, exceptions, final_code)


def wait_for_element_is_not_present(element, wait_time=settings.time_of_element_disappearence):
    return wait_for_element(lambda: element.is_present(), lambda is_present: not is_present, wait_time=wait_time)


def wait_for_element_is_not_visible(element, wait_time=settings.time_of_element_disappearence):
    return wait_for_element(lambda: element.is_visible(), lambda is_visible: not is_visible, wait_time=wait_time)


def wait_for_ajax():
    """
    Wait for jQuery is completed. This method requires additional testing.
    :return: self
    """

    def ajax():
        try:
            import selene
            return selene.execute_script('return jQuery.isReady')
        except WebDriverException:
            return True

    wait_for_element(ajax, lambda result: result, wait_time=settings.time_of_element_disappearence)
