from __future__ import annotations

from typing import Any, Dict, List, Tuple, cast

import pytest
from _pytest.monkeypatch import MonkeyPatch

from selene.support.conditions import have


Call = Tuple[str, Tuple[Any, ...], Dict[str, Any]]


class FakeCondition:
    def __init__(self, calls: List[Call]):
        self.calls = calls

    def value(self, *args: Any, **kwargs: Any) -> 'FakeCondition':
        return FakeCondition(self.calls + [('value', args, kwargs)])

    def value_containing(self, *args: Any, **kwargs: Any) -> 'FakeCondition':
        return FakeCondition(self.calls + [('value_containing', args, kwargs)])

    def values(self, *args: Any, **kwargs: Any) -> 'FakeCondition':
        return FakeCondition(self.calls + [('values', args, kwargs)])

    def values_containing(self, *args: Any, **kwargs: Any) -> 'FakeCondition':
        return FakeCondition(self.calls + [('values_containing', args, kwargs)])


class FakeMatch:
    def __getattr__(self, factory_name: str):
        def factory(*args: Any, **kwargs: Any) -> FakeCondition:
            return FakeCondition([(factory_name, args, kwargs)])

        return factory


@pytest.fixture
def fake_match(monkeypatch: MonkeyPatch) -> FakeMatch:
    fake = FakeMatch()
    monkeypatch.setattr(have, 'match', fake)
    return fake


def assert_delegated(actual: object, expected_calls: List[Call]) -> None:
    fake_actual = cast(FakeCondition, actual)

    assert fake_actual.calls == expected_calls


@pytest.mark.parametrize(
    ('builder_name', 'args', 'factory_name'),
    [
        ('exact_text', ('Hello',), 'element_has_exact_text'),
        ('text', ('ell',), 'element_has_text'),
        ('value', ('42',), 'element_has_value'),
        ('values', ('a', 'b'), 'collection_has_values'),
        ('value_containing', ('4',), 'element_has_value_containing'),
        (
            'values_containing',
            ('a', 'b'),
            'collection_has_values_containing',
        ),
        ('css_class', ('active',), 'element_has_css_class'),
        ('tag', ('button',), 'element_has_tag'),
        ('tag_containing', ('but',), 'element_has_tag_containing'),
        ('size', (2,), 'collection_has_size'),
        ('size_less_than', (2,), 'collection_has_size_less_than'),
        (
            'size_less_than_or_equal',
            (2,),
            'collection_has_size_less_than_or_equal',
        ),
        ('size_greater_than', (2,), 'collection_has_size_greater_than'),
        (
            'size_greater_than_or_equal',
            (2,),
            'collection_has_size_greater_than_or_equal',
        ),
        ('texts', ('a', 'b'), 'collection_has_texts'),
        ('exact_texts', ('a', 'b'), 'collection_has_exact_texts'),
        ('url', ('https://example.test',), 'browser_has_url'),
        ('url_containing', ('example',), 'browser_has_url_containing'),
        ('title', ('Example',), 'browser_has_title'),
        ('title_containing', ('Exam',), 'browser_has_title_containing'),
        ('tabs_number', (2,), 'browser_has_tabs_number'),
        (
            'tabs_number_less_than',
            (2,),
            'browser_has_tabs_number_less_than',
        ),
        (
            'tabs_number_less_than_or_equal',
            (2,),
            'browser_has_tabs_number_less_than_or_equal',
        ),
        (
            'tabs_number_greater_than',
            (2,),
            'browser_has_tabs_number_greater_than',
        ),
        (
            'tabs_number_greater_than_or_equal',
            (2,),
            'browser_has_tabs_number_greater_than_or_equal',
        ),
        (
            'script_returned',
            (True, 'return arguments[0]', 1),
            'browser_has_script_returned',
        ),
    ],
)
def test_simple_factories_delegate_to_match(
    fake_match: FakeMatch,
    builder_name: str,
    args: Tuple[Any, ...],
    factory_name: str,
) -> None:
    actual = getattr(have, builder_name)(*args)

    assert_delegated(actual, [(factory_name, args, {})])


@pytest.mark.parametrize(
    ('builder_name', 'factory_name'),
    [
        ('attribute', 'element_has_attribute'),
        ('js_property', 'element_has_js_property'),
        ('css_property', 'element_has_css_property'),
    ],
)
def test_property_builders_delegate_to_match_without_value(
    fake_match: FakeMatch,
    builder_name: str,
    factory_name: str,
) -> None:
    actual = getattr(have, builder_name)('name')

    assert_delegated(actual, [(factory_name, ('name',), {})])


@pytest.mark.parametrize(
    ('builder_name', 'factory_name'),
    [
        ('attribute', 'element_has_attribute'),
        ('js_property', 'element_has_js_property'),
        ('css_property', 'element_has_css_property'),
    ],
)
def test_property_builders_accept_deprecated_positional_value(
    fake_match: FakeMatch,
    builder_name: str,
    factory_name: str,
) -> None:
    with pytest.warns(DeprecationWarning):
        actual = getattr(have, builder_name)('name', 'expected')

    assert_delegated(
        actual,
        [
            (factory_name, ('name',), {}),
            ('value', ('expected',), {}),
        ],
    )


def test_size_at_least_warns_and_delegates_to_greater_than_or_equal(
    fake_match: FakeMatch,
) -> None:
    with pytest.warns(PendingDeprecationWarning):
        actual = have.size_at_least(2)

    assert_delegated(
        actual,
        [('collection_has_size_greater_than_or_equal', (2,), {})],
    )


def test_js_returned_true_warns_and_delegates_to_script_returned(
    fake_match: FakeMatch,
) -> None:
    with pytest.warns(DeprecationWarning):
        actual = have.js_returned_true('return true')

    assert_delegated(
        actual,
        [('browser_has_script_returned', (True, 'return true'), {})],
    )


def test_js_returned_warns_and_delegates_to_script_returned(
    fake_match: FakeMatch,
) -> None:
    with pytest.warns(DeprecationWarning):
        actual = have.js_returned(42, 'return arguments[0]', 'arg')

    assert_delegated(
        actual,
        [('browser_has_script_returned', (42, 'return arguments[0]', 'arg'), {})],
    )
