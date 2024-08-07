# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
from __future__ import annotations

import functools
import warnings
from typing import Iterable

from typing_extensions import overload, Union, Callable, Optional, Tuple, Type

from selene.common._typing_functions import Query, E, R


class TimeoutException(AssertionError):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        return exception_msg


# TODO: should we extend it from SeleneError and make lazy in same way?
#       probably not just from SeleneError,
#       cause not all SeleneErrors are assertion errors
class ConditionMismatch(AssertionError):
    """An error to through during assertion if the asserting condition is not matched.

    Contains a bunch of factory methods to transform regular predicates
    (functions that returns True/False) into condition functions
    that raise this error (ConditionMismatch) where predicate would return false.

    Is handy for building custom expected conditions for explicit waits and assertions.
    See a practical examples of application in
    [Expected Conditions][expected-conditions] guide.

    Examples of usage of factory methods:

    ```python
    # GIVEN
    class predicate:
        @staticmethod
        def is_positive(x) -> bool:
            return x > 0

    def is_positive(x) -> bool:
        return x > 0

    def decremented(x) -> int:
        return x - 1

    # THEN (all will pass without error)
    ConditionMismatch.to_raise_if_not(predicate.is_positive)(1)
    ConditionMismatch.to_raise_if_not(is_positive)(1)
    ConditionMismatch.to_raise_if(predicate.is_positive)(0)
    ConditionMismatch.to_raise_if(is_positive)(0)

    ConditionMismatch.to_raise_if_not(Query('is positive', lambda x: x > 0))(1)
    ConditionMismatch.to_raise_if(Query('is positive', lambda x: x > 0))(0)

    ConditionMismatch.to_raise_if_not(
        Query('is positive', lambda x: x > 0),
        Query('decremented', lambda x: x - 1),
    )(2)
    ConditionMismatch.to_raise_if_not(
        Query('is positive', lambda x: x > 0),
        decremented,
    )(2)
    ConditionMismatch.to_raise_if_not(is_positive, decremented)(2)
    ConditionMismatch.to_raise_if(is_positive, decremented)(1)
    ConditionMismatch.to_raise_if_not(actual=decremented, by=is_positive)(2)
    ConditionMismatch.to_raise_if(actual=decremented, by=is_positive)(1)

    ConditionMismatch.to_raise_if_not_actual(decremented, predicate.is_positive)(2)
    ConditionMismatch.to_raise_if_actual(decremented, predicate.is_positive)(1)
    ConditionMismatch.to_raise_if_not_actual(decremented, predicate.is_positive)(2)
    ConditionMismatch.to_raise_if_actual(decremented, is_positive)(1)

    ConditionMismatch.to_raise_if_not_actual(
        Query('decremented', lambda x: x - 1),
        Query('is positive', lambda x: x > 0)
    )(2)
    # ...
    ```
    """  # todo: document _describe_actual_result examples

    def __init__(self, message='condition not matched'):
        super().__init__(message)

    @classmethod
    @overload
    def _to_raise_if_not(
        cls,
        by: Callable[[E], bool],
        *,
        _inverted: bool = False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @classmethod
    @overload
    def _to_raise_if_not(
        cls,
        by: Callable[[R], bool],
        actual: Callable[[E], R] | None = None,
        *,
        _describe_actual_result: Callable[[R], str] | None = None,
        _inverted: bool = False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    # TODO: should we name test param as predicate?
    @classmethod
    def _to_raise_if_not(
        cls,
        by: Callable[[E | R], bool],
        # todo: should we provide lambda it: it as default to actual?
        actual: Callable[[E], E | R] | None = None,
        *,
        # we can't name it:
        # - as `describe` because it will not be clear what are we going to describe
        #   is it a description of the result of the whole comparison? or what?
        # - as `describe_actual` because it will not be clear:
        #   do we describe actual as a query? or as a result of the query being called?
        #     - Hm... BUT! actual is also not named as `actual_query` but just `actual`
        #         maybe then `describe_actual` is a better name, because then
        #         it can be used even if actual is not provided
        #         then it will be applied directly to the entity...
        #       Hm... maybe, even `describe` will work then...
        # todo: but should we name it regardless of "actual" arg presence?
        #       should not we allow to use it when actual is not provided?
        #       so it's applied to raw entity, same way as by will be...
        _describe_actual_result: Callable[[E | R], str] | None = None,
        _inverted: Optional[bool] = False,
        # todo: should we rename it to _exceptions_as_truthy_on_inverted?
        #       or just document this in docstring?
        #       – seems like no, because now falsy are always falsy:)
        #       as we started to differentiate raising falsy from raising non-falsy
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        @functools.wraps(by)  # todo: should we also count non-none actual fn in wraps?
        def wrapped(entity: E) -> None:
            def describe_not_match(actual_value):
                describe_actual_result = _describe_actual_result or (
                    lambda value: (
                        Query._full_description_or(
                            'actual', for_=actual, _with_prefix='actual '
                        )
                        + f': {value}'
                    )
                )
                return (
                    describe_actual_result(actual_value)
                    if actual
                    else (
                        (
                            (
                                (f'not ({name})' if _inverted else name)
                                if (name := Query._full_description_for(by))
                                else ''
                            )
                            or "condition"
                        )
                        + ' not matched'
                        # TODO: should we consider eliminating errors like:
                        #       'Reason: ConditionMismatch: condition not matched\n'
                        #       to:
                        #       'Reason: ConditionMismatch\n'
                    )
                    # TODO: decide on
                    #       cls(f'{Query.full_name_for(predicate) or "condition"} not matched')
                    #       vs
                    #       else cls('condition not matched')
                )

            def describe_error(error):
                # TODO: should not we remove/add stacktrace somewhere in Wait? not here?
                #       or do it only for _falsy_exceptions?
                # todo: consider making it customizable
                # remove stacktrace if available:
                stacktrace = getattr(error, 'stacktrace', None)
                return (
                    str(error)
                    if not stacktrace
                    else (
                        ''.join(
                            str(error).split('\n'.join(['Stacktrace:', *stacktrace]))
                        )
                    )
                )

            actual_to_test = None
            try:
                actual_to_test = actual(entity) if actual else entity
            except Exception as reason:
                is_falsy = any(
                    isinstance(reason, exception) for exception in _falsy_exceptions
                )
                if _inverted and is_falsy:
                    return
                # only _falsy_exceptions can be considered as "condition mismatch"
                # others should signify the "total comparison is invalid in this case" failure
                # todo: should we rebuild reason if it's not is_falsy
                #       by applying describe_error like we did further below?
                raise (cls(describe_error(reason)) if is_falsy else reason) from reason

            answer = None
            try:
                answer = by(actual_to_test)
            # todo: should we move Exception processing out of this helper?
            #       should it be somewhere in Condition?
            #       cause now it's not a Mismatch anymore, it's a failure
            #       – no, we should not, we should keep it here,
            #         because this is needed for the inverted case
            except Exception as reason:
                is_falsy = any(
                    isinstance(reason, exception) for exception in _falsy_exceptions
                )
                if _inverted and is_falsy:
                    return
                # answer is still None
                raise (cls if is_falsy else reason.__class__)(
                    # todo: should we still remove stacktrace from reason
                    #       if it's not is_falsy?
                    f'{describe_error(reason)}:'
                    f'\n{describe_not_match(actual_to_test)}'
                ) from reason

            if answer if _inverted else not answer:
                # TODO: should we render expected too? (based on predicate name)
                #       we want need it for our conditions,
                #       cause wait.py logs it in the message
                #       but ... ?
                raise cls(describe_not_match(actual_to_test))

        return wrapped

    @classmethod
    def _to_raise_if(
        cls,
        by: Callable[[E | R], bool],
        actual: Callable[[E], E | R] | None = None,
        *,
        _describe_actual_result: Callable[[E | R], str] | None = None,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        return cls._to_raise_if_not(
            by,
            actual,
            _describe_actual_result=_describe_actual_result,
            _inverted=True,
            _falsy_exceptions=_falsy_exceptions,
        )

    @classmethod
    def _to_raise_if_not_actual(
        cls,
        query: Callable[[E], R],
        by: Callable[[R], bool],
        *,
        _describe_actual_result: Callable[[R], str] | None = None,
    ):
        return cls._to_raise_if_not(
            by, query, _describe_actual_result=_describe_actual_result
        )

    @classmethod
    def _to_raise_if_actual(
        cls,
        query: Callable[[E], R],
        by: Callable[[R], bool],
        *,
        _describe_actual_result: Callable[[R], str] | None = None,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        return cls._to_raise_if(
            by,
            query,
            _describe_actual_result=_describe_actual_result,
            _falsy_exceptions=_falsy_exceptions,
        )


class ConditionNotMatchedError(ConditionMismatch):
    def __init__(self, message='condition not matched'):
        warnings.warn(
            'ConditionNotMatchedError is deprecated, use ConditionMismatch instead',
            DeprecationWarning,
        )
        super().__init__(message)

    def __init_subclass__(cls, **kwargs):
        warnings.warn(
            'ConditionNotMatchedError is deprecated, use ConditionMismatch instead',
            DeprecationWarning,
        )
        super().__init_subclass__(**kwargs)


# TODO: should we name it *Error or *Exception?
#       (see
#        https://www.python.org/dev/peps/pep-0008/#exception-names
#        https://www.datacamp.com/community/tutorials/exception-handling-python
#       )
#       should we name it simply Error and allow to import as selene.Error ?
#       should we name it SeleneError and still allow to import as selene.Error?
class _SeleneError(AssertionError):
    def __init__(self, message: Union[str, Callable[[], str]]):
        self._render_message: Callable[[], str] = lambda: (
            message() if callable(message) else message
        )

    @property
    def args(self):
        return (self._render_message(),)

    def __str__(self):
        return self._render_message()

    def __repr__(self):
        return f"SeleneError: {self._render_message()}"
