import inspect
import typing
import dataclasses

MISSING = object()
_FIELDS = getattr(dataclasses, '_FIELDS', '__dataclass_fields__')
_POST_INIT_NAME = getattr(dataclasses, '_POST_INIT_NAME', '__post_init__')


# todo: add support for InitVar and ClassVar like in original dataclasses


def _set_new_attribute(cls, name, value):
    """
    Never overwrites an existing attribute.  Returns True if the
    attribute already exists.
    """
    if name in cls.__dict__:
        return True
    setattr(cls, name, value)
    return False


T = typing.TypeVar('T')


@dataclasses.dataclass
class Box(typing.Generic[T]):
    value: T


class Boxed:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name).value

    def __set__(self, instance, value):
        if not hasattr(instance, self.name):
            if isinstance(value, Box):
                setattr(instance, self.name, value)
            else:
                setattr(instance, self.name, Box(value))
        else:
            getattr(instance, self.name).value = value


class _Field:
    def __init__(self, name: str, type_: type, default):
        if isinstance(default, (list, dict, set)):
            raise ValueError(
                f"Don't use mutable type {type(default)} as a default for field {name}"
            )

        self.name = name
        self.type_ = type_
        self.default = default

        # for some compatibility with original dataclasses
        self.init = True
        self.default_factory = MISSING
        self._field_type = dataclasses._FIELD

    @property
    def has_default(self) -> bool:
        return self.default is not MISSING

    @property
    def as_init_arg(self) -> str:
        maybe_default = f'={self.named_default}' if self.has_default else ''
        return f'{self.name}: {self.named_type}{maybe_default}'

    @property
    def as_assignment(self) -> str:
        return f'self.{self.name} = {self.name}'

    @property
    def named_default(self) -> str:
        return f'_dflt_of_{self.name}'

    @property
    def named_type(self) -> str:
        return f'_type_of_{self.name}'

    @staticmethod
    def s_from(cls):
        return [
            _Field(name, type_, getattr(cls, name, MISSING))
            for name, type_ in getattr(cls, '__annotations__', {}).items()
        ]

    @property
    def box_name(self):
        return f'__boxed_{self.name}'

    def new_boxed_descriptor(self):
        return Boxed(self.box_name)


def dataclass(cls):
    fields = _Field.s_from(cls)
    setattr(cls, _FIELDS, dict((f.name, f) for f in fields))

    locals_ = {}
    init_args = []

    for field in fields:
        locals_[field.named_type] = field.type_
        if field.has_default:
            locals_[field.named_default] = field.default

        init_args.append(field.as_init_arg)

    has_post_init = hasattr(cls, _POST_INIT_NAME)
    post_init_params_str = ','.join(
        field.name
        for field in fields
        if field._field_type is dataclasses._FIELD_INITVAR
    )

    wrapper_fn = '\n'.join(
        [
            f'def wrapper({", ".join(locals_.keys())}):',
            f' def __init__(self, {", ".join(init_args)}):',
            '\n'.join(
                [
                    *[f'  {field.as_assignment}' for field in fields],
                    *(
                        [
                            f'  self.{dataclasses._POST_INIT_NAME}({post_init_params_str})'
                        ]
                        if has_post_init
                        else []
                    ),
                ]
            )
            or '  pass',
            f' return __init__',
        ]
    )

    namespace = {}
    exec(wrapper_fn, None, namespace)

    init_fn = namespace['wrapper'](**locals_)

    _set_new_attribute(cls, '__init__', init_fn)

    print('fields: ', fields)
    for field in fields:
        setattr(cls, field.name, field.new_boxed_descriptor())

    if not getattr(cls, '__doc__'):
        cls.__doc__ = cls.__name__ + str(inspect.signature(cls)).replace(
            ' -> None', ''
        )

    return cls


def replace(obj, /, **changes):
    """Return a new object replacing specified fields with new values.

    Example usage:

      @dataclass
      class C:
          x: int
          y: int

      c = C(1, 2)
      c1 = replace(c, x=3)
      assert c1.x == 3 and c1.y == 2
    """

    if not dataclasses._is_dataclass_instance(obj):
        raise TypeError('replace() should be called on dataclass instances')

    # If a field is not in 'changes', read its value from the provided obj.
    for f in getattr(obj, _FIELDS).values():
        # Only consider normal fields or InitVars.
        if f._field_type is dataclasses._FIELD_CLASSVAR:
            continue

        if not f.init:
            if f.name in changes:
                raise ValueError(
                    f'field {f.name} is declared with '
                    'init=False, it cannot be specified with '
                    'replace()'
                )
            continue

        if f.name not in changes:
            if (
                f._field_type is dataclasses._FIELD_INITVAR
                and f.default is MISSING
            ):
                raise ValueError(
                    f"InitVar {f.name!r} " 'must be specified with replace()'
                )
            changes[f.name] = getattr(obj, f.box_name)

    return obj.__class__(**changes)
