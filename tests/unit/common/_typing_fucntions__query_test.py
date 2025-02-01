from __future__ import annotations

import pytest

from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import Query


def test_query_name_and_application():
    ...

    is_positive = Query('is positive', lambda x: x > 0)

    assert 'is positive' == str(is_positive)
    assert is_positive(1) == True
    assert is_positive(0) == False


def test_query_recomposition():
    ...

    is_positive_increented_by = lambda number: Query(
        f'is positive incremented by {number}', lambda x: x + number > 0
    )

    assert 'is positive incremented by 0' == str(is_positive_increented_by(0))
    assert is_positive_increented_by(0)(0) == False
    assert is_positive_increented_by(1)(0) == True
    assert is_positive_increented_by(1)(-1) == False
    assert is_positive_increented_by(2)(-1) == True

    # TODO: consider the is_positive_increented_by(1).as('is increment positive') syntax
    is_increment_positive = Query('is increment positive', is_positive_increented_by(1))

    assert 'is increment positive' == str(is_increment_positive)
    assert is_increment_positive(0) == True
    assert is_increment_positive(-1) == False
