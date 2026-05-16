import pytest
import sys
import importlib

from selene.core.condition import Condition, not_
from selene.core.exceptions import ConditionNotMatchedError


def test_by_and_passes_when_all_conditions_pass():
    first = Condition(
        'first is positive',
        lambda x: (
            None if x > 0 else (_ for _ in ()).throw(AssertionError('first failed'))
        ),
    )
    second = Condition(
        'second is less than 10',
        lambda x: (
            None if x < 10 else (_ for _ in ()).throw(AssertionError('second failed'))
        ),
    )

    combined = Condition.by_and(first, second)

    combined.call(5)
    assert str(combined) == 'first is positive and second is less than 10'


def test_by_and_stops_on_first_failed_condition():
    calls = []

    def fail_first(entity):
        calls.append('first')
        raise AssertionError('first failed')

    def never_called(entity):
        calls.append('second')

    combined = Condition.by_and(
        Condition('first', fail_first),
        Condition('second', never_called),
    )

    with pytest.raises(AssertionError, match='first failed'):
        combined.call(1)
    assert calls == ['first']


def test_by_or_passes_when_any_condition_passes():
    first = Condition(
        'first fails', lambda _: (_ for _ in ()).throw(AssertionError('first failed'))
    )
    second = Condition('second passes', lambda _: None)
    combined = Condition.by_or(first, second)

    combined.call('entity')
    assert str(combined) == 'first fails or second passes'


def test_by_or_raises_aggregated_errors_when_all_fail():
    first = Condition(
        'first fails', lambda _: (_ for _ in ()).throw(AssertionError('first failed'))
    )
    second = Condition(
        'second fails', lambda _: (_ for _ in ()).throw(ValueError('second failed'))
    )
    combined = Condition.by_or(first, second)

    with pytest.raises(AssertionError, match='first failed; second failed'):
        combined.call('entity')


def test_for_each_passes_when_all_items_match():
    positive = Condition(
        'is positive',
        lambda x: (
            None if x > 0 else (_ for _ in ()).throw(AssertionError('not positive'))
        ),
    )

    per_item = Condition.for_each(positive)

    per_item.call([1, 2, 3])
    assert str(per_item) == ' each is positive'


def test_for_each_reports_items_and_indexes_on_failures():
    positive = Condition(
        'is positive',
        lambda x: (
            None if x > 0 else (_ for _ in ()).throw(AssertionError('not positive'))
        ),
    )
    per_item = Condition.for_each(positive)

    with pytest.raises(AssertionError) as error:
        per_item.call([2, -1, -3])

    message = str(error.value)
    assert 'indexes from 0 to 2' in message
    assert '-1: not positive' in message
    assert '-3: not positive' in message


def test_as_not_inverts_condition_and_uses_default_description():
    is_even = Condition(
        'is even',
        lambda x: (
            None if x % 2 == 0 else (_ for _ in ()).throw(AssertionError('not even'))
        ),
    )
    inverted = Condition.as_not(is_even)

    inverted.call(3)
    assert str(inverted) == 'is not (even)'

    with pytest.raises(ConditionNotMatchedError):
        inverted.call(2)


def test_as_not_supports_custom_description():
    original = Condition('has value', lambda _: None)
    inverted = Condition.as_not(original, description='has no value')

    assert str(inverted) == 'has no value'


def test_raise_if_not_raises_condition_not_matched_error():
    condition = Condition.raise_if_not('is truthy', lambda x: bool(x))

    condition.call(1)
    with pytest.raises(ConditionNotMatchedError):
        condition.call(0)


def test_raise_if_not_actual_uses_function_name_in_error_message():
    def length_of(value):
        return len(value)

    condition = Condition.raise_if_not_actual(
        'length is 3',
        length_of,
        lambda actual: actual == 3,
    )

    with pytest.raises(AssertionError, match='actual length_of: 2'):
        condition.call('ab')


def test_raise_if_not_actual_uses_query_string_for_callable_object():
    class Query:
        def __call__(self, value):
            return len(value)

        def __str__(self):
            return 'query length'

    condition = Condition.raise_if_not_actual(
        'length is 3',
        Query(),
        lambda actual: actual == 3,
    )

    with pytest.raises(AssertionError, match='actual query length: 2'):
        condition.call('ab')


def test_raise_if_not_actual_passes_when_predicate_matches():
    condition = Condition.raise_if_not_actual(
        'length is 2',
        lambda value: len(value),
        lambda actual: actual == 2,
    )

    condition.call('ab')


def test_predicate_returns_true_or_false_without_reraising():
    failing = Condition('fails', lambda _: (_ for _ in ()).throw(RuntimeError('boom')))
    passing = Condition('passes', lambda _: None)

    assert failing.predicate('entity') is False
    assert passing.predicate('entity') is True


def test_not_alias_not_property_and_each_property_work():
    base = Condition(
        'is positive',
        lambda x: (
            None if x > 0 else (_ for _ in ()).throw(AssertionError('not positive'))
        ),
    )
    always = Condition('always', lambda _: None)

    assert isinstance(base.not_, Condition)
    assert isinstance(not_(base), Condition)
    assert isinstance(base.each, Condition)
    assert isinstance(base.or_(always), Condition)


def test_condition_module_uses_typing_callable_on_python_lt_310(monkeypatch):
    import selene.core.condition as condition_module

    original_version_info = sys.version_info
    monkeypatch.setattr(sys, 'version_info', (3, 9, 18, 'final', 0))
    reloaded = importlib.reload(condition_module)

    try:
        assert reloaded.Callable is not None
    finally:
        monkeypatch.setattr(sys, 'version_info', original_version_info)
        importlib.reload(condition_module)
