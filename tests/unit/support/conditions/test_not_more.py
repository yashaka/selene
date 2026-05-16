import pytest

from typing import Any, Dict, List, Tuple, cast

from selene.support.conditions import not_ as not_conditions

Call = Tuple[str, Tuple[Any, ...], Dict[str, Any]]
NOT_CALL: Call = ('not_', (), {})


class FakeCondition:
    def __init__(self, calls: List[Call]):
        self.calls = calls

    @property
    def not_(self) -> 'FakeCondition':
        return FakeCondition(self.calls + [NOT_CALL])

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
def fake_match(monkeypatch):
    fake = FakeMatch()
    monkeypatch.setattr(not_conditions, '_match', fake)
    return fake


def assert_negated(actual: object, expected_calls_before_not: List[Call]) -> None:
    fake_actual = cast(FakeCondition, actual)

    assert fake_actual.calls == expected_calls_before_not + [NOT_CALL]


def test_attribute_builder_exposes_negated_value_variants(fake_match):
    attribute = not_conditions.attribute('href')

    assert_negated(
        attribute.value('/login'),
        [
            ('element_has_attribute', ('href',), {}),
            ('value', ('/login', False), {}),
        ],
    )
    assert_negated(
        attribute.value_containing('login', ignore_case=True),
        [
            ('element_has_attribute', ('href',), {}),
            ('value_containing', ('login', True), {}),
        ],
    )
    assert_negated(
        attribute.values('/a', '/b'),
        [
            ('element_has_attribute', ('href',), {}),
            ('values', ('/a', '/b'), {}),
        ],
    )
    assert_negated(
        attribute.values_containing('a', 'b'),
        [
            ('element_has_attribute', ('href',), {}),
            ('values_containing', ('a', 'b'), {}),
        ],
    )


@pytest.mark.parametrize(
    ('builder_name', 'factory_name'),
    [
        ('js_property', 'element_has_js_property'),
        ('css_property', 'element_has_css_property'),
    ],
)
def test_property_builders_expose_negated_value_variants(
    fake_match,
    builder_name,
    factory_name,
):
    prop = getattr(not_conditions, builder_name)('name')

    assert_negated(
        prop.value('expected'),
        [
            (factory_name, ('name',), {}),
            ('value', ('expected',), {}),
        ],
    )
    assert_negated(
        prop.value_containing('part'),
        [
            (factory_name, ('name',), {}),
            ('value_containing', ('part',), {}),
        ],
    )
    assert_negated(
        prop.values('a', 'b'),
        [
            (factory_name, ('name',), {}),
            ('values', ('a', 'b'), {}),
        ],
    )
    assert_negated(
        prop.values_containing('a', 'b'),
        [
            (factory_name, ('name',), {}),
            ('values_containing', ('a', 'b'), {}),
        ],
    )


@pytest.mark.parametrize(
    ('builder_name', 'factory_name'),
    [
        ('attribute', 'element_has_attribute'),
        ('js_property', 'element_has_js_property'),
        ('css_property', 'element_has_css_property'),
    ],
)
def test_property_builders_accept_deprecated_positional_value(
    fake_match,
    builder_name,
    factory_name,
):
    with pytest.warns(DeprecationWarning):
        actual = getattr(not_conditions, builder_name)('name', 'expected')

    assert_negated(
        actual,
        [
            (factory_name, ('name',), {}),
            ('value', ('expected',), {}),
        ],
    )


@pytest.mark.parametrize(
    ('builder_name', 'factory_name'),
    [
        ('attribute', 'element_has_attribute'),
        ('js_property', 'element_has_js_property'),
        ('css_property', 'element_has_css_property'),
    ],
)
def test_property_builders_accept_deprecated_keyword_value(
    fake_match,
    builder_name,
    factory_name,
):
    with pytest.warns(DeprecationWarning):
        actual = getattr(not_conditions, builder_name)('name', value='expected')

    assert_negated(
        actual,
        [
            (factory_name, ('name',), {}),
            ('value', ('expected',), {}),
        ],
    )


@pytest.mark.parametrize(
    ('builder_name', 'args', 'factory_name'),
    [
        ('exact_text', ('Hello',), 'element_has_exact_text'),
        ('text', ('ell',), 'element_has_text'),
        ('value', ('42',), 'element_has_value'),
        ('value_containing', ('4',), 'element_has_value_containing'),
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
            'js_returned',
            (True, 'return arguments[0]', 1),
            'browser_has_js_returned',
        ),
    ],
)
def test_simple_factories_delegate_to_match_and_invert(
    fake_match,
    builder_name,
    args,
    factory_name,
):
    actual = getattr(not_conditions, builder_name)(*args)

    assert_negated(actual, [(factory_name, args, {})])


def test_size_at_least_warns_and_delegates_to_greater_than_or_equal(fake_match):
    with pytest.warns(PendingDeprecationWarning):
        actual = not_conditions.size_at_least(2)

    assert_negated(
        actual,
        [('collection_has_size_greater_than_or_equal', (2,), {})],
    )


def test_js_returned_true_warns_and_delegates_to_js_returned(fake_match):
    with pytest.warns(PendingDeprecationWarning):
        actual = not_conditions.js_returned_true('return true')

    assert_negated(
        actual,
        [('browser_has_js_returned', (True, 'return true'), {})],
    )
