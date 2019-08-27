# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import six
import time
from selenium.common.exceptions import TimeoutException

from selene.abctypes.conditions import IEntityCondition


def wait_for(entity, condition, timeout=4, polling=0.1):
    # type: (object, IEntityCondition, int) -> object
    end_time = time.time() + timeout
    while True:
        try:
            return condition.fn(entity)
        except Exception as reason:
            reason_message = str(reason)
            # reason_message = getattr(reason, 'msg',  # todo: is the previous line enough?
            #                          getattr(reason, 'message',
            #                                  getattr(reason, 'args', '')))

            if six.PY2:
                if isinstance(reason_message, unicode):
                    reason_message = reason_message.encode('unicode-escape')
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
