from selene.common import predicate


def test_is_truthy_treats_empty_string_as_truthy_and_others_by_bool():
    assert predicate.is_truthy('') is True
    assert predicate.is_truthy(0) is False
    assert predicate.is_truthy('ok') is True


def test_equals_and_equals_ignoring_case():
    assert predicate.equals('A')('A') is True
    assert predicate.equals('A')('a') is False
    nested = predicate.equals('A', ignore_case=True)('a')
    assert callable(nested)
    assert nested('a') is True
    assert predicate.equals_ignoring_case('A')('a') is True


def test_order_predicates():
    assert predicate.is_greater_than(1)(2) is True
    assert predicate.is_greater_than_or_equal(2)(2) is True
    assert predicate.is_less_than(3)(2) is True
    assert predicate.is_less_than_or_equal(2)(2) is True


def test_includes_variants_and_type_error_path():
    assert predicate.includes('el')('selene') is True
    nested = predicate.includes('EL', ignore_case=True)('selene')
    assert callable(nested)
    assert nested('selene') is True
    assert predicate.includes_ignoring_case('EL')('selene') is True
    assert predicate.includes('x')(None) is False


def test_includes_word_variants():
    assert predicate.includes_word('hello')('hello world') is True
    nested = predicate.includes_word('HELLO', ignore_case=True)('hello world')
    assert callable(nested)
    assert nested('hello world') is True
    assert predicate.includes_word_ignoring_case('HELLO')('hello world') is True
