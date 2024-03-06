from __future__ import annotations
from selene.core.wait import Wait


# TODO: break down into actual unit tests or move elsewhere as e2e
def test_simple_waiting_entity_lifecycle__when_fn_is_static_fn():
    # GIVEN
    class Entity:
        def __init__(self, attribute=None):
            self.attribute = attribute
            self.wait = Wait(self, at_most=0.5)

        def with_attribute(self, attribute):
            self.attribute = attribute
            return self

        def __str__(self):
            return f'Entity({self.attribute})'

    class have:
        @staticmethod
        def attribute(entity: Entity):
            if entity.attribute is None:
                raise AssertionError('attribute is None')
            return entity

    entity = Entity('some value')

    # WHEN
    result = entity.wait.for_(have.attribute)

    # THEN passed with returned same entity editable “fluently” in place
    changed_result = result.with_attribute(None)

    # WHEN
    try:
        changed_result.wait.for_(have.attribute)

    # THEN
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert (
            'Entity(None)'
            f'.{test_simple_waiting_entity_lifecycle__when_fn_is_static_fn.__name__}'
            '.<locals>'
            '.have.attribute'
        ) in str(error)
        assert 'Reason: AssertionError: attribute is None' in str(error)

    # WHEN
    have.attribute.__qualname__ = 'has attribute defined'
    # AND
    try:
        changed_result.wait.for_(have.attribute)

    # THEN new __qualname__ value is used in error message
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert 'Entity(None).has attribute defined' in str(error)
        assert 'Reason: AssertionError: attribute is None' in str(error)

    # WHEN
    have.attribute.__str__ = lambda: 'has defined attribute'
    # AND
    try:
        changed_result.wait.for_(have.attribute)

    # THEN __qualname__ still overrides __str__ in error message
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert 'Entity(None).has defined attribute' not in str(error)  # <- THEN
        assert 'Entity(None).has attribute defined' in str(error)  # <- THEN
        assert 'Reason: AssertionError: attribute is None' in str(error)


def test_simple_waiting_entity_lifecycle__when_fn_is_callable():
    # GIVEN
    class Entity:
        def __init__(self, attribute=None):
            self.attribute = attribute
            self.wait = Wait(self, at_most=0.5)

        def with_attribute(self, attribute):
            self.attribute = attribute
            return self

        def __str__(self):
            return f'Entity({self.attribute})'

    class HaveAttribute:
        def __call__(self, entity: Entity):
            if entity.attribute is None:
                raise AssertionError('attribute is None')
            return entity

    have_attribute = HaveAttribute()

    entity = Entity('some value')

    # WHEN
    result = entity.wait.for_(have_attribute)

    # THEN passed with returned same entity editable “fluently” in place
    changed_result = result.with_attribute(None)

    # WHEN
    try:
        changed_result.wait.for_(have_attribute)

    # THEN
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert (
            'Entity(None)'
            f'.<tests.unit.core.test_wait'
            f'.{test_simple_waiting_entity_lifecycle__when_fn_is_callable.__name__}'
            '.<locals>'
            '.HaveAttribute object at'
        ) in str(error)
        assert 'Reason: AssertionError: attribute is None' in str(error)

    # WHEN
    have_attribute.__str__ = lambda: 'has defined attribute'
    # AND
    try:
        changed_result.wait.for_(have_attribute)

    # THEN __str__() in error message
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert 'Entity(None).has defined attribute' in str(error)  # <- THEN
        assert 'Reason: AssertionError: attribute is None' in str(error)

    # WHEN
    have_attribute.__qualname__ = 'has attribute defined'
    # AND
    try:
        changed_result.wait.for_(have_attribute)

    # THEN new __qualname__ overrides __str__()
    except AssertionError as error:
        assert 'Timed out after 0.5s, while waiting for:' in str(error)
        assert 'Entity(None).has attribute defined' in str(error)  # <- THEN
        assert 'Reason: AssertionError: attribute is None' in str(error)
