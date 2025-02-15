def test_either__returns_failure():
    from selene.common.fp import _either

    result, maybe_failure = _either(
        lambda numbers: numbers[3],
        or_=IndexError,
    )([1, 2, 3])

    assert isinstance(maybe_failure, IndexError)
    assert str(maybe_failure) == 'list index out of range'
    assert not result


def test_either__returns_result():
    from selene.common.fp import _either

    result, maybe_failure = _either(
        lambda numbers: numbers[2],
        or_=IndexError,
    )([1, 2, 3])

    assert result == 3
    assert not maybe_failure
