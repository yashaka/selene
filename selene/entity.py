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

from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TypeVar

from selene.config import Config
from selene.wait import Wait, Command, Query
from selene.condition import Condition

E = TypeVar('E', bound='Assertable')
R = TypeVar('R')


class Assertable(ABC):
    @abstractmethod
    def should(self, condition: Condition[E]) -> E:
        pass


# todo: try as Matchable(ABC) and check if autocomplete will still work
class Matchable(Assertable):
    @abstractmethod
    def wait_until(self, condition: Condition[E]) -> bool:
        pass

    @abstractmethod
    def matching(self, condition: Condition[E]) -> bool:
        pass


class Configured(ABC):
    @property
    @abstractmethod
    def config(self) -> Config:
        pass


class WaitingEntity(Matchable, Configured):

    def __init__(self, config: Config):
        self._config = config
        self._wait = Wait(self,
                          at_most=config.timeout,
                          or_fail_with=config.hooks.wait.failure)

    @property
    def wait(self) -> Wait[E]:
        return self._wait

    def perform(self, command: Command[E]) -> E:
        """Useful to call external commands.

        Commands might be predefined in Selene:
            element.perform(command.js.scroll_into_view)
        or some custom defined by selene user:
            element.perform(my_action.triple_click)

        You might think that it will be usefull to use these methods also in Selene internally
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

    def get(self, query: Query[E, R]) -> R:
        return self.wait.for_(query)

    # --- Configured --- #

    @property
    def config(self) -> Config:
        return self._config

    # --- Assertable --- #

    def should(self, condition: Condition[E]) -> E:
        self.wait.for_(condition)
        return self

    # --- Matchable --- #

    def wait_until(self, condition: Condition[E]) -> bool:
        return self.wait.until(condition)

    def matching(self, condition: Condition[E]) -> bool:
        return condition.predicate(self)
