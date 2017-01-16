import selene
import selene.tools
from selene import config
# from selene.elements import SeleneElement, SeleneCollection

import time
from selenium.common.exceptions import TimeoutException

from selene.abctypes.conditions import IEntityCondition
from selene.exceptions import ConditionMismatchException


def wait_for(entity, condition, timeout=4, polling=0.1):
    # type: (object, IEntityCondition, int) -> object
    end_time = time.time() + timeout
    while True:
        try:
            return condition.fn(entity)
        except Exception as reason:
            reason_message = getattr(reason, 'msg', getattr(reason, 'message', ''))
            reason_string = '{name}: {message}'.format(name=reason.__class__.__name__, message=reason_message)
            screen = getattr(reason, 'screen', None)
            stacktrace = getattr(reason, 'stacktrace', None)

            if time.time() > end_time:
                raise TimeoutException('''
            failed while waiting {timeout} seconds
            to assert {condition}
            for {entity}

            reason: {reason}'''.format(
                    timeout=timeout,
                    condition=condition.description(),
                    entity=entity,
                    reason=reason_string), screen, stacktrace)

            time.sleep(polling)


def satisfied(entity, condition):
    try:
        value = condition(entity)
        return value if value is not None else False
    except Exception as exc:
        return False
