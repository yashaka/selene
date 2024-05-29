from __future__ import annotations

from selene.core.condition import Condition
import pytest

from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import E, Query


def test_match__of_constructed_via__init():
    positive = Condition(
        'match positive',
        ConditionMismatch._to_raise_if_not(Query('is positive', lambda x: x > 0)),
        _inverted=False,
    )

    positive._match(1)
    assert 'match positive' == str(positive)

    try:
        positive._match(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'is positive not matched' == str(error)


def test_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive._match(1)
    assert 'is positive' == str(positive)

    try:
        positive._match(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_match__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    positive._match(1)
    assert 'is positive' == str(positive)

    try:
        positive._match(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_predicate__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    assert positive.predicate(1)
    assert not positive.predicate(0)


def test_not_match__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    positive.not_._match(0)

    try:
        positive.not_._match(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_not_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive.not_._match(0)
    assert 'is not (positive)' == str(positive.not_)

    try:
        positive.not_._match(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


# TODO: should the feature be implemented?
def x_test_not_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition(
        'is positive',
        ConditionMismatch._to_raise_if_not(lambda actual: actual > 0),
        _query=Query('self', lambda it: it),  # 💡
    )

    positive.not_._match(0)
    assert 'is not (positive)' == str(positive.not_)

    try:
        positive.not_._match(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)  # 💡


def test_not_not_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive.not_.not_._match(1)
    assert 'is positive' == str(positive.not_.not_)

    try:
        positive.not_.not_._match(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_as_not_match__of_constructed_via_factory__raise_if_not_actual():
    # GIVEN ConditionMismatch default behavior (just to compare the difference)
    try:
        ConditionMismatch._to_raise_if_not_actual(
            Query('self', lambda it: it), lambda actual: actual > 0
        )(1)
    except AssertionError as error:
        assert 'actual self: 1' == str(error)

    # AND
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda actual: actual), lambda it: it > 0
    )

    # WHEN
    negative_or_zero = Condition.as_not(positive, 'negative or zero')

    # THEN
    assert 'negative or zero' == str(negative_or_zero)
    negative_or_zero._match(0)

    # WHEN
    try:
        negative_or_zero._match(1)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)
        # # TODO: do we need the following behavior?
        # assert 'actual self: 1' == str(error)
