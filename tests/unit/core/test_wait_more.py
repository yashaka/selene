import pytest

from selene.core.exceptions import TimeoutException
from selene.core.wait import Wait


def test_wait_entity_deprecated_alias_returns_entity_and_warns():
    wait = Wait('entity', at_most=0.01)

    with pytest.warns(DeprecationWarning):
        assert wait._entity == 'entity'


def test_wait_at_most_returns_new_wait_with_new_timeout():
    wait = Wait('entity', at_most=1.0)

    changed = wait.at_most(2.5)

    assert changed is not wait
    assert changed.entity == 'entity'
    assert changed._timeout == 2.5


def test_wait_or_fail_with_and_hook_failure_property_are_applied():
    def custom_hook(error: TimeoutException) -> Exception:
        return RuntimeError(f'hooked: {error.msg}')

    wait = Wait('entity', at_most=0.0).or_fail_with(custom_hook)

    assert wait.hook_failure is custom_hook

    with pytest.raises(RuntimeError, match='hooked:'):
        wait.for_(lambda _: (_ for _ in ()).throw(AssertionError('boom')))


def test_wait_until_returns_true_on_success_and_false_on_timeout():
    wait = Wait('entity', at_most=0.0)

    assert wait.until(lambda _: 'ok') is True
    assert wait.until(lambda _: (_ for _ in ()).throw(AssertionError('boom'))) is False


def test_wait_command_executes_command_wrapper():
    state = {'called': False}
    wait = Wait(state, at_most=0.01)

    wait.command('mark called', lambda entity: entity.__setitem__('called', True))

    assert state['called'] is True


def test_wait_query_executes_query_wrapper_and_returns_value():
    wait = Wait('hello', at_most=0.01)

    result = wait.query('length', lambda text: len(text))

    assert result == 5


def test_wait_for_timeout_message_uses_error_alias_for_pattern_error_name():
    class PatternError(Exception):
        pass

    wait = Wait('entity', at_most=0.0)

    def always_fails(_):
        error = PatternError('bad pattern')
        error.msg = 'bad pattern'
        raise error

    with pytest.raises(TimeoutException) as caught:
        wait.for_(always_fails)

    assert 'Reason: error: bad pattern' in caught.value.msg
