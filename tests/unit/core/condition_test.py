from __future__ import annotations

from selene.core.condition import Condition, Match
import pytest

from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import Query


def test_match__of_constructed_via__init__with_test_fn():
    positive = Condition(
        'positive',
        ConditionMismatch._to_raise_if_not(Query('is positive', lambda x: x > 0)),
    )

    positive._test(1)
    assert 'positive' == str(positive)

    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'is positive not matched' == str(error)


def test_match__of_constructed_via__init__with_test_by_predicate_as_lambda():
    positive = Match(
        'positive',
        by=lambda x: x > 0,
    )

    positive._test(1)
    assert 'positive' == str(positive)

    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_match__of_constructed_via__init__with_test_by_predicate_as_query():
    positive = Match(
        'positive',
        by=Query('is positive', lambda x: x > 0),
    )

    positive._test(1)
    assert 'positive' == str(positive)

    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'is positive not matched' == str(error)


def test_match__of_constructed_via__init__with_test_by_query_and_actual_as_lambda():
    positive_decrement = Match(
        'positive decrement',
        actual=lambda x: x - 1,
        by=Query('is positive', lambda x: x > 0),
    )

    positive_decrement._test(2)
    assert 'positive decrement' == str(positive_decrement)

    try:
        positive_decrement._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual: 0' == str(error)


def test_match__of_constructed_via__init__with_test_by_query_and_actual_as_query():
    positive_decrement = Match(
        'positive decrement',
        actual=Query('decrement', lambda x: x - 1),
        by=Query('is positive', lambda x: x > 0),
    )

    positive_decrement._test(2)
    assert 'positive decrement' == str(positive_decrement)

    try:
        positive_decrement._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual decrement: 0' == str(error)


# TODO: consider implenting
def x_test_match__of_constructed_via__init__with_test_by_and_actual_but_no_desc():
    positive_decrement = Match(
        by=Query('has positive', lambda x: x > 0),
        actual=Query('decrement', lambda x: x - 1),
    )

    positive_decrement._test(2)
    assert 'has positive decrement' == str(positive_decrement)

    try:
        positive_decrement._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual decrement: 0' == str(error)


# TODO: consider implenting
def x_test_match__of_constructed_via__init__with_test_by_n_actual_as_tuples_n_no_desc():
    positive_decrement = Match(
        actual=('decrement', lambda x: x - 1),
        by=('is positive', lambda x: x > 0),
    )

    positive_decrement._test(2)
    assert 'is positive decrement' == str(positive_decrement)

    try:
        positive_decrement._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual decrement: 0' == str(error)


def test_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive._test(1)
    assert 'is positive' == str(positive)

    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_match__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    positive._test(1)
    assert 'is positive' == str(positive)

    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_predicate__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    assert positive.predicate(1)
    assert not positive.predicate(0)


def test_not_match__of_constructed_via_factory__raise_if_not():
    positive = Condition.raise_if_not('is positive', lambda actual: actual > 0)

    positive.not_._test(0)

    try:
        positive.not_._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_not_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive.not_._test(0)
    assert 'is not (positive)' == str(positive.not_)

    try:
        positive.not_._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)


def test_not_match__of_constructed_via_Condition__init__with__predicate_and_query():
    positive = Condition(
        'is positive',
        _actual=Query('self', lambda it: it),
        _by=lambda actual: actual > 0,
    )

    positive.not_._test(0)
    assert 'is not (positive)' == str(positive.not_)

    try:
        positive.not_._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)


def test_not_match__of_constructed_via_Match__init__with__predicate_and_query():
    positive = Match(
        'is positive',
        actual=Query('self', lambda it: it),
        by=lambda actual: actual > 0,
    )

    positive.not_._test(0)
    assert 'is not (positive)' == str(positive.not_)

    try:
        positive.not_._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)


def test_not_not_match__of_constructed_via_factory__raise_if_not_actual():
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda it: it), lambda actual: actual > 0
    )

    positive.not_.not_._test(1)
    assert 'is positive' == str(positive.not_.not_)

    try:
        positive.not_.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_not_not_match__of_constructed_via_Condition__init__():
    positive = Condition(
        'is positive',
        _actual=Query('self', lambda it: it),
        _by=lambda actual: actual > 0,
    )

    positive.not_.not_._test(1)
    assert 'is positive' == str(positive.not_.not_)

    try:
        positive.not_.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_not_not_match__of_constructed_via_Match__init__():
    positive = Match(
        'is positive', actual=Query('self', lambda it: it), by=lambda actual: actual > 0
    )

    positive.not_.not_._test(1)
    assert 'is positive' == str(positive.not_.not_)

    try:
        positive.not_.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)


def test_as_not_renamed_match__of_constructed_via_factory__raise_if_not_actual():
    # GIVEN ConditionMismatch default behavior (just to compare the difference)
    try:
        ConditionMismatch._to_raise_if_not_actual(
            Query('self', lambda it: it), lambda actual: actual > 0
        )(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)

    # AND
    positive = Condition.raise_if_not_actual(
        'is positive', Query('self', lambda actual: actual), lambda it: it > 0
    )

    # WHEN
    negative_or_zero = Condition.as_not(positive, 'negative or zero')

    # THEN
    assert 'negative or zero' == str(negative_or_zero)
    negative_or_zero._test(0)

    # WHEN
    try:
        negative_or_zero._test(1)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        # assert 'actual self: 1' == str(error)  # TODO: can we achieve this?
        assert 'actual self: 1' == str(error)


def test_Condition__init__renamed_match_not__of_constructed_via__Condition__test():
    # GIVEN
    positive = Condition(
        'is positive',
        ConditionMismatch._to_raise_if_not_actual(
            Query('self', lambda actual: actual), lambda it: it > 0
        ),
    )
    assert 'is positive' == str(positive)
    positive._test(1)
    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)

    # WHEN "rebuilt with new name"
    negative_or_zero = Condition('negative or zero', positive.not_)
    # THEN
    assert 'negative or zero' == str(negative_or_zero)
    negative_or_zero._test(0)
    # WHEN
    try:
        negative_or_zero._test(1)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)

    # WHEN inverted the "rebuilt inversion"
    not_negative_or_zero = negative_or_zero.not_
    # THEN
    assert 'not (negative or zero)' == str(not_negative_or_zero)
    not_negative_or_zero._test(1)
    # WHEN
    try:
        not_negative_or_zero._test(0)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test_Match__init__renamed_match_not__of_constructed_via__Match__actual_by():
    # GIVEN
    positive = Match(
        'is positive',
        Query('self', lambda actual: actual),
        by=lambda it: it > 0,
    )
    assert 'is positive' == str(positive)
    positive._test(1)
    try:
        positive._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)

    # WHEN "rebuilt with new name"
    negative_or_zero = Match('negative or zero', by=positive.not_)
    # THEN
    assert 'negative or zero' == str(negative_or_zero)
    negative_or_zero._test(0)
    # WHEN
    try:
        negative_or_zero._test(1)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)

    # WHEN inverted the "rebuilt inversion"
    not_negative_or_zero = negative_or_zero.not_
    # THEN
    assert 'not (negative or zero)' == str(not_negative_or_zero)
    not_negative_or_zero._test(1)
    # WHEN
    try:
        not_negative_or_zero._test(0)
        # THEN
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


def test___init__renamed_match_not__of_constructed_via__init__actual_by_compared():
    # GIVEN ConditionMismatch default behavior (just to compare the difference)
    try:
        ConditionMismatch._to_raise_if_not_actual(
            Query('self', lambda it: it), lambda actual: actual > 0
        )(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)

    # AND
    positive__via_test = Condition(
        'is positive',
        ConditionMismatch._to_raise_if_not_actual(
            Query('self', lambda actual: actual), lambda it: it > 0
        ),
    )
    positive__via_actual_by = Condition(
        'is positive',
        _actual=Query('self', lambda actual: actual),
        _by=lambda it: it > 0,
    )

    # WHEN as is

    # THEN
    # - compare name
    assert 'is positive' == str(positive__via_test)
    assert 'is positive' == str(positive__via_actual_by)
    # - compare pass
    positive__via_test._test(1)
    positive__via_actual_by._test(1)
    # - compare fail
    try:
        positive__via_test._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)
    try:
        positive__via_actual_by._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 0' == str(error)

    # WHEN "rebuilt with new name"
    negative_or_zero__from_via_actual_by__inverted_then_rebuilt = Condition(
        'negative or zero', positive__via_actual_by.not_
    )
    negative_or_zero__from_via_actual_by__rebuilt_via_as_not = Condition.as_not(
        positive__via_actual_by, 'negative or zero'
    )
    negative_or_zero__from_via_test__inverted_then_rebuilt = Condition(
        'negative or zero', positive__via_test.not_
    )
    negative_or_zero__from_via_test__rebuilt_via_as_not = Condition.as_not(
        positive__via_test, 'negative or zero'
    )
    # THEN
    # - compare name
    assert 'negative or zero' == str(
        negative_or_zero__from_via_actual_by__inverted_then_rebuilt
    )
    assert 'negative or zero' == str(
        negative_or_zero__from_via_actual_by__rebuilt_via_as_not
    )
    assert 'negative or zero' == str(
        negative_or_zero__from_via_test__inverted_then_rebuilt
    )
    assert 'negative or zero' == str(
        negative_or_zero__from_via_test__rebuilt_via_as_not
    )
    # - compare pass
    negative_or_zero__from_via_actual_by__inverted_then_rebuilt._test(0)
    negative_or_zero__from_via_actual_by__rebuilt_via_as_not._test(0)
    negative_or_zero__from_via_test__inverted_then_rebuilt._test(0)
    negative_or_zero__from_via_test__rebuilt_via_as_not._test(0)
    # - compare fail
    try:
        negative_or_zero__from_via_actual_by__inverted_then_rebuilt._test(1)  # 🏆
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)  # ⬅️ ↗️
    try:
        negative_or_zero__from_via_actual_by__rebuilt_via_as_not._test(1)  # 🏆
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'actual self: 1' == str(error)  # ⬅️ ↗️
    try:
        negative_or_zero__from_via_test__inverted_then_rebuilt._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)
    try:
        negative_or_zero__from_via_test__rebuilt_via_as_not._test(1)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)

    # WHEN will invert the rebuilt version
    # THEN
    # - compare name
    # - compare name
    assert 'not (negative or zero)' == str(
        negative_or_zero__from_via_actual_by__inverted_then_rebuilt.not_
    )
    assert 'not (negative or zero)' == str(
        negative_or_zero__from_via_actual_by__rebuilt_via_as_not.not_
    )
    assert 'not (negative or zero)' == str(
        negative_or_zero__from_via_test__inverted_then_rebuilt.not_
    )
    assert 'not (negative or zero)' == str(
        negative_or_zero__from_via_test__rebuilt_via_as_not.not_
    )
    # - compare pass
    negative_or_zero__from_via_actual_by__inverted_then_rebuilt.not_._test(1)
    negative_or_zero__from_via_actual_by__rebuilt_via_as_not.not_._test(1)
    negative_or_zero__from_via_test__inverted_then_rebuilt.not_._test(1)
    negative_or_zero__from_via_test__rebuilt_via_as_not.not_._test(1)
    # - compare fail
    try:
        negative_or_zero__from_via_actual_by__inverted_then_rebuilt.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        # assert 'actual self: 0' == str(error)  # todo: can we achieve this?
        assert 'condition not matched' == str(error)  # 😢
    try:
        negative_or_zero__from_via_actual_by__rebuilt_via_as_not.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)
    try:
        negative_or_zero__from_via_test__inverted_then_rebuilt.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)
    try:
        negative_or_zero__from_via_test__rebuilt_via_as_not.not_._test(0)
        pytest.fail('on mismatch')
    except AssertionError as error:
        assert 'condition not matched' == str(error)


# TODO: add InvalidCompareError tests (positive and negative)

# TODO: cover subclass based conditions
