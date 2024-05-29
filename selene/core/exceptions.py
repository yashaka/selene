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
from typing import Union, Callable

from typing_extensions import Any, override, overload, TypeVar

from selene.common._typing_functions import Query

R = TypeVar('R')
E = TypeVar('E')

# from selene.core.wait import E, R, Query


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
    """
    Examples of application

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

    # THEN
    ConditionMismatch.to_raise_if_not_actual(predicate.is_positive)(1)
    ConditionMismatch.to_raise_if_not_actual(is_positive)(1)
    ConditionMismatch.to_raise_if_not(predicate.is_positive)(1)  # ❤️
    ConditionMismatch.to_raise_if_not(is_positive)(1)  # ❤️

    ConditionMismatch.to_raise_if_not_actual(Query('is positive', lambda x: x > 0))(1)
    ConditionMismatch.to_raise_if_not(Query('is positive', lambda x: x > 0))(1)  # ❤️

    ConditionMismatch.to_raise_if_not(Query('is positive', lambda x: x > 0), decremented)(1)  # ❤️
    ConditionMismatch.to_raise_if_not(is_positive, decremented)(1)  # ❤️
    ConditionMismatch.to_raise_if_not(decremented, is_positive)(1)
    ConditionMismatch.to_raise_if_not_actual(decremented, is_positive)(1)  # ❤
    ```
    """

    @classmethod
    @overload
    def _to_raise_if_not(cls, test: Callable[[E], bool]): ...

    @classmethod
    @overload
    def _to_raise_if_not(cls, test: Callable[[R], bool], actual: Callable[[E], R]): ...

    # TODO: should we name test param as predicate?
    @classmethod
    def _to_raise_if_not(
        cls,
        # TODO: test may sound like assertion, not predicate... rename?
        test: Callable[[E | R], bool],
        actual: Callable[[E], E | R] | None = None,
        # TODO: should we add inverted here?
    ):
        @functools.wraps(test)
        def wrapped(entity: E) -> None:
            actual_description = (
                f' {name}' if (name := Query.full_name_for(actual)) else ''
            )
            actual_to_test = actual(entity) if actual else entity
            if not test(actual_to_test):
                # TODO: should we render expected too? (based on predicate name)
                raise (
                    cls(f'actual{actual_description}: {actual_to_test}')
                    if actual
                    else cls(f'{Query.full_name_for(test) or "condition"} not matched')
                    # TODO: decide on
                    #       cls(f'{Query.full_name_for(predicate) or "condition"} not matched')
                    #       vs
                    #       else cls('condition not matched')
                )

        return wrapped

    @classmethod
    def _to_raise_if_not_actual(
        cls,
        query: Callable[[E], R],
        test: Callable[[R], bool],
    ):
        return cls._to_raise_if_not(test, query)

    # @classmethod
    # def to_raise_if_not(
    #     cls,
    #     predicate: Callable[[Any], bool],
    #     _named: str | None = None,
    #     _message: str | None = None,
    # ):
    #     @functools.wraps(predicate)
    #     def wrapped(x):
    #         nonlocal predicate
    #         if not predicate(x):
    #             raise cls(
    #                 _message
    #                 if _message
    #                 else f"{_named if _named else predicate} not matched"
    #             )
    #
    #     return wrapped

    def __init__(self, message='condition not matched'):
        super().__init__(message)


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
