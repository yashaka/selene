# MIT License
#
# Copyright (c) 2015 Iakiv Kramarenko
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

import warnings
from abc import ABC, abstractmethod
import typing_extensions as typing
from typing_extensions import Self, Optional, TypeVar

from selene.common._typing_functions import Command, Query
from selene.core.condition import Condition
from selene.core.configuration import Config
from selene.core.locator import Locator
from selene.core.wait import Wait


# TODO: can we remove it? and call super().__init__() directly inside _Entity?
class _Mixin:
    def __init__(self, **kwargs):
        super().__init__()


# TODO: consider moving to selene.common.mixinish.py
# TODO: could and should we make it generic on TypeDict reflecting kwargs types?
# todo: is the Entity name – the best? maybe Model? Shape?
class _Entity(_Mixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kwargs_ = kwargs

    def _build_(self, **kwargs) -> Self:
        # TODO: when upgraded to python 3.9 refactor to self.__class__(**(self._kwargs | kwargs))
        return self.__class__(**{**self._kwargs_, **kwargs})


LR = TypeVar('LR')
"""Reflects "locatee" – the result of location by Locator instance"""


class _LocatableEntity(_Entity, typing.Generic[LR]):
    def __init__(self, *, locator: Locator[LR], **kwargs):
        super().__init__(locator=locator, **kwargs)
        self._locator = locator

    def locate(self) -> LR:
        return self._locator()

    def __str__(self):
        return str(self._locator)

    def __call__(self, *args, **kwargs):
        return self.locate()

    @property
    def _raw_(self):
        warnings.warn(
            'entity._raw_ might become deprecated, '
            'use entity.locate() or entity() instead',
            FutureWarning,
        )
        return self.locate()


# TODO: won't Protocol be better here? (instead of ABC)
# todo: should we move it to their own module? (with Matchable and Assertable)
class Assertable(ABC):
    # TODO: Should not we accept here also Callable[[Self], None]?
    @abstractmethod
    def should(self, condition: Condition[Self]) -> Self:
        pass


class Matchable(ABC):
    @abstractmethod
    def wait_until(self, condition: Condition[Self]) -> bool:
        pass

    @abstractmethod
    def matching(self, condition: Condition[Self]) -> bool:
        pass


class _ConfiguredEntity(_Entity):
    def __init__(self, config: Config, **kwargs):
        super().__init__(config=config, **kwargs)
        self._config = config

    @property
    def config(self) -> Config:
        return self._config

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Self:
        return self._build_(
            config=config if config else self.config.with_(**config_as_kwargs),
        )


R = TypeVar('R')
"""Reflects a result of a query"""


# TODO: should we bind it to Configured? it looks like can be more versatile...
class _WaitingConfiguredEntity(_ConfiguredEntity, Assertable, Matchable):
    def __init__(self, config: Config, **kwargs):
        super().__init__(config=config, **kwargs)

    @property
    def wait(self) -> Wait[Self]:
        return self.config._wait(self)

    # TODO: could we pass commands that are narrower than Self?
    def perform(self, command: Command[Self]) -> Self:
        """Useful to call external commands.

        Commands might be predefined in Selene:
            element.perform(command.js.scroll_into_view)
        or some custom defined by selene user:
            element.perform(my_action.triple_click)

        You might think that it will be useful
        to use these methods also in Selene internally
        in order to define built in commands e.g. in Element class, like:

            def click(self):
                return self.perform(Command('click', lambda element: element().click()))

        instead of:

            def click(self):
                self.wait.for_(Command('click', lambda element: element().click()))
                return self

        But so far, we use the latter version - though, less concise, but more explicit,
        making it more obvious that waiting is built in;)

        """
        self.wait.for_(command)
        return self

    # TODO: what about `entity[query.something]` syntax
    #       over or in addition to `entity.get(query.something)` ?
    def get(self, query: Query[Self, R]) -> R | None:  # TODO: why | None?
        return (
            self.wait.with_(decorator=None)
            if self.config._disable_wait_decorator_on_get_query
            else self.wait
        ).for_(query)

    # --- Assertable --- #

    def should(self, condition: Condition[Self]) -> Self:
        self.wait.for_(condition)
        return self

    # --- Matchable --- #

    def wait_until(self, condition: Condition[Self]) -> bool:
        return self.wait.until(condition)

    def matching(self, condition: Condition[Self]) -> bool:
        return condition.predicate(self)


# TODO: consider _LazyCachableLocatableEntity?
class _CachedLocatableEntity(_LocatableEntity[LR]):
    def __init__(self, locator: Locator[LR], **kwargs):
        super().__init__(locator=locator, **kwargs)

    @property
    def cached(self) -> Self:
        cache = None
        error = None
        try:
            cache = self.locate()
        except Exception as e:
            error = e

        def get_cache():
            if cache:
                return cache
            raise error

        return self._build_(locator=Locator(f'{self}.cached', get_cache))
