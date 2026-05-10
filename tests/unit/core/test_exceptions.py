import pytest

from selene.core.exceptions import TimeoutException, ConditionNotMatchedError, _SeleneError


def test_timeout_exception_str_includes_message_prefix_and_newline():
    error = TimeoutException('boom')

    assert str(error) == 'Message: boom\n'


def test_condition_not_matched_error_default_message():
    error = ConditionNotMatchedError()

    assert str(error) == 'condition not matched'


def test_condition_not_matched_error_custom_message():
    error = ConditionNotMatchedError('custom failure')

    assert str(error) == 'custom failure'


def test_selene_error_with_static_message_in_args_str_and_repr():
    error = _SeleneError('static message')

    assert error.args == ('static message',)
    assert str(error) == 'static message'
    assert repr(error) == 'SeleneError: static message'


def test_selene_error_with_lazy_callable_message_is_evaluated_lazily_per_access():
    calls = {'count': 0}

    def lazy_message():
        calls['count'] += 1
        return f'lazy #{calls["count"]}'

    error = _SeleneError(lazy_message)

    # every access renders again by design
    assert error.args == ('lazy #1',)
    assert str(error) == 'lazy #2'
    assert repr(error) == 'SeleneError: lazy #3'


def test_selene_error_propagates_callable_errors():
    def broken_message():
        raise RuntimeError('cannot render message')

    error = _SeleneError(broken_message)

    with pytest.raises(RuntimeError, match='cannot render message'):
        _ = str(error)
