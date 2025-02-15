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
"""
Currently this is a temporal module for backward-compatible imports.
"""
# TODO: consider deprecating and then removing exported things from this module
from __future__ import annotations

from typing_extensions import (
    Iterable,
)

from selene.core._entity import (
    _WaitingConfiguredEntity,
    Assertable as __AssertableAlias,
    Matchable as __MatchableAlias,
    _ConfiguredEntity as __ConfiguredEntityAlias,
)
from selene.core._element import Element as _ElementAlias
from selene.core._elements import All


WaitingEntity = _WaitingConfiguredEntity


def _is_element(obj: object) -> bool:
    return (
        isinstance(obj, _WaitingConfiguredEntity)
        and hasattr(obj, 'locate')
        and not isinstance(obj, Iterable)
    )


def _is_collection(obj: object) -> bool:
    return (
        isinstance(obj, _WaitingConfiguredEntity)
        and hasattr(obj, 'locate')
        and isinstance(obj, Iterable)
    )


def _wraps_driver(obj: object) -> bool:
    return isinstance(obj, _WaitingConfiguredEntity) and hasattr(obj, 'driver')


# --- Things to consider for deprecatioin and removal ---
# TODO: make them "simulating generic" where needed
Assertable = __AssertableAlias
Matchable = __MatchableAlias
Configured = __ConfiguredEntityAlias
Element = _ElementAlias


# TODO: are there any better place for this "alias"?
class Collection(
    All[Element],
):
    def __init__(self, locator, config, _Element=Element, **kwargs):
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            **kwargs,
        )
