from selenium.common.exceptions import StaleElementReferenceException
from selene import config
from selene.condition_helpers import satisfied
from selene.helpers import suppress


def wait_for(code=lambda: None, until=lambda code_result: code_result.is_displayed(), after=lambda: None,
             wait_time=config.default_wait_time):
    """
    waits `wait_time` smartly for the `until` conditions to be satisfied on the result of executing `code`
    but after the `after` code was executed initially
    """
    # todo: think on: letting the wait_for to accept hamcrest matchers as 'until' conditions

    conditions = until if isinstance(until, (tuple, list)) else [until]
    import stopit
    import time

    # todo: catch 'all' possible relevant exceptions below...
    # todo: it was assumed that after() will not be needed once exception was encountered... Though this needs to be proved...
    with suppress(StaleElementReferenceException):
        result = code()
        if conditions and not satisfied(result, *conditions):
            after()

    # todo: think on: refactoring to match at once the result to all conditions combined into one
    #       since it will check conditions one by one, one after another... and in the final end, some previous
    #       conditions may not be met already...
    for condition_met in conditions:
        with stopit.ThreadingTimeout(wait_time) as to_ctx_mgr, suppress(StaleElementReferenceException):
            while not condition_met(result):
                time.sleep(0.1)
                result = code()
        if not to_ctx_mgr:
            err_message = """
            Timeout reached while waiting...
            During: %ss
            For: <TBD>
            Until: %s
            """ % (wait_time, condition_met.__name__)
            raise stopit.TimeoutException(err_message)
            # todo: improve error message. Also taking into account the proper alternative of condition implementation

    return result