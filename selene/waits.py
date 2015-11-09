import os
from httplib import CannotSendRequest

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from selene import config
from selene.condition_helpers import satisfied
from selene.driver import browser
from selene.helpers import suppress, take_screenshot


class DummyResult(object):
    def __getattr__(self, item):
        return lambda *args, **kwargs: False


def wait_for(code=lambda: None, until=lambda code_result: True, by_demand_after=lambda: None,
             wait_time=config.default_wait_time):
    """
    waits `wait_time` smartly for the `until` conditions to be satisfied on the result of executing `code`
    but after the `after` code was executed optionally in case code() gave no satisfied result at first attempt

    :param code - in case hasattr(code, 'to_str') to_str() method will be called to stringify code at error message in
    case of failed wait_for
    """
    # todo: think on: better name for by_demand_after, or even another way to implement this feature
    # todo: think on: letting the wait_for to accept hamcrest matchers as 'until' conditions
    # todo: think on: renaming 'code' param to element_finder in case wait_for will be only "element wait" implementation.
    #       the `code` name was chosen in order to implement "general case" of waiter
    #       nevertheless, the wait_for implementation has some parts bounded to the "element finding" context,
    #           like throwing specific exception in case element was not found...

    conditions = until if isinstance(until, (tuple, list)) else [until]
    import stopit
    import time

    # todo: catch 'all' possible relevant exceptions below...
    # todo: it was assumed that after() will not be needed once exception was encountered... Though this needs to be proved...
    # todo:     and documented
    result = DummyResult()
    with suppress(StaleElementReferenceException, NoSuchElementException, CannotSendRequest):
        result = code()
        if conditions and not satisfied(result, *conditions):
            by_demand_after()

    # todo: think on: refactoring to match at once the result to all conditions combined into one
    #       since it will check conditions one by one, one after another... and in the final end, some previous
    #       conditions may not be met already...
    for condition_met in conditions:
        with stopit.ThreadingTimeout(wait_time) as to_ctx_mgr:
            while not condition_met(result):
                with suppress(StaleElementReferenceException, NoSuchElementException, CannotSendRequest):
                    time.sleep(0.1)
                    result = code()
        if not to_ctx_mgr:
            # todo: think on: refactor the following code, make it just `raise stopit.TimeoutException(repr(code))` or etc.
            # todo: make the following 'screenshot taking' code optional (controoled via config)
            # todo: think on: unbinding screenshooting from the wait_for implementation
            screenshot = '%s.png' % time.time()
            path = os.path.abspath('./reports/screenshots')  # todo: make screenshots path configurable
            full_path = take_screenshot(browser(), screenshot, path)

            err_message = """
            Timeout reached while waiting...
            During: %ss
            For: %s
            Until: %s
            Screenshot: %s
            """ % (wait_time,
                   code.__name__,  # todo: think on: refactoring to the usage without "underscores"
                   condition_met.__name__,
                   full_path)
            raise stopit.TimeoutException(err_message)
            # todo: improve error message. Also taking into account the proper alternative of condition implementation
            #       e.g. as hamcrest matchers

    return result
