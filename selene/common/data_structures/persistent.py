import inspect
import typing
import dataclasses

# from types import GenericAlias

MISSING = object()
_FIELDS = getattr(dataclasses, '_FIELDS', '__dataclass_fields__')
_POST_INIT_NAME = getattr(dataclasses, '_POST_INIT_NAME', '__post_init__')


# TODO: add support for InitVar and ClassVar like in original dataclasses


def _set_new_attribute(cls, name, value):
    """
    Never overwrites an existing attribute.  Returns True if the
    attribute already exists.
    """
    if name in cls.__dict__:
        return True
    setattr(cls, name, value)
    return False


def _with_setattr(obj, attribute, value):
    setattr(obj, attribute, value)
    return obj


T = typing.TypeVar('T')


@dataclasses.dataclass
class Box(typing.Generic[T]):
    value: T


class Boxed:
    def __init__(
        self, name=None
    ):  # currently we allways pass name in this persistent.py
        self.name = name

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name).value

    def __set__(self, instance, value):
        if not hasattr(instance, self.name):
            if isinstance(value, Box):
                setattr(instance, self.name, value)
            elif inspect.isdatadescriptor(value):
                # try to find default inside descriptor
                default = getattr(value, 'default', None)
                if default is not None:
                    setattr(instance, self.name, Box(default))
                    return
                # try to get default from __get__
                if hasattr(value, '__get__'):
                    try:
                        default = value.__get__(instance, owner=type(instance))
                        if default:
                            setattr(instance, self.name, Box(default))
                            return
                    except Exception:
                        pass
                raise TypeError(
                    f"__init__() missing required argument to be stored as: '{value.name}'"
                    f"or cannot find default value for descriptor: {value} "
                    f"(default should be provided "
                    f"either by 'default' attribute or by __get__ method)"
                )
            else:
                setattr(instance, self.name, Box(value))
        else:
            getattr(instance, self.name).value = value


class Field:
    def __init__(self, name: str, type_: type, default):
        if isinstance(default, (list, dict, set)):
            raise ValueError(
                f"Don't use mutable type {type(default)} as a default for field {name}"
            )

        self.name = name
        self.type_ = type_
        self.default = default

        # for some compatibility with original dataclasses (not used in this impl)
        self.init = True
        self.default_factory = MISSING
        self._field_type = getattr(dataclasses, '_FIELD')

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name

        # Forward __set_name__ to the field default if it is a descriptor.
        set_name = getattr(type(self.default), '__set_name__', None)
        if set_name:
            # There is a __set_name__ method on the descriptor, call
            # it.
            set_name(self.default, owner, self.box_mask(name))

    @property
    def has_default(self) -> bool:
        return self.default is not MISSING

    @property
    def has_default_as_descriptor(self) -> bool:
        return self.has_default and inspect.isdatadescriptor(self.default)

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
    def from_(class_, name: str, type_: type):
        default = getattr(class_, name, MISSING)
        if isinstance(default, Field):
            # supporting attributes with default as field() instance
            a_field = default
            a_field.name = name
            a_field.type_ = type_
        else:
            # – default was passed directly as a value to class attribute...
            # Thus, if default is a descriptor with __set_name__,
            # its name is incorrect and may lead to recursion on usage.
            # To fix this we should mutate default.name.
            # We could do this later,
            # once field instance provides its descriptor on request,
            # when calling field.descriptor...
            # More over, we could not mutate original descriptor,
            # but create a copy or even a new descriptor decorating original one
            # and providing fixed name, while providing delegate access to all other attributes.
            # ...
            # But since we have separate forwarding logic in __set_name__
            # for the case when descriptor is passed explicitly as a field default,
            # lets for less confusion and KISS, for now, just mutate it below:
            a_field = Field(name, type_, default)
            if a_field.has_default_as_descriptor:
                setattr(a_field.default, 'name', a_field.box_name)

        return a_field

    @staticmethod
    def s_from(class_):
        return [
            Field.from_(class_, name, type_)
            for name, type_ in getattr(class_, '__annotations__', {}).items()
        ]

    @staticmethod
    def box_mask(name):
        return f'__boxed_{name}'

    @staticmethod
    def value_from(obj, attribute):
        return getattr(obj, Field.box_mask(attribute)).value

    @property
    def box_name(self):
        return self.box_mask(self.name)

    @property
    def descriptor(self):
        return (
            Boxed(self.box_name)
            if not self.has_default_as_descriptor
            else _with_setattr(self.default, 'name', self.box_name)
        )

    # __class_getitem__ = classmethod(GenericAlias)


# This function is used instead of exposing Field creation directly,
# so that a type checker can be told (via overloads) that this is a
# function whose type depends on its parameters.
def field(
    *,
    default=MISSING,
    # default_factory=MISSING,
    # init=True,
    # repr=True,
    # hash=None,
    # compare=True,
    # metadata=None,
):
    # if default is not MISSING and default_factory is not MISSING:
    #     raise ValueError('cannot specify both default and default_factory')

    return Field(
        name=...,
        type_=...,
        default=default,  # , default_factory, init, repr, hash, compare, metadata
    )


def dataclass(cls):
    """
    Generates __init__ method for the `cls`
    based on type annotations and class attributes with default values.
    Provides a `Boxed` descriptor for each field,
    which persists the reference to the field value
    after object was «cloned» via `replace` method.

    The custom descriptor can be provided:
    * as default value
      * e.g. `nickname: str = ToUpperDescriptor()`
    * or explicit field with default value
      * e.g. `nickname: str = field(default=ToUpperDescriptor())` .
    Then this descriptor will be used instead of `Boxed` descriptor
    to provide get and set access to the field value.
    Take into account, that this custom descriptor
    should handle situation when user forgot to set the required argument
    on object creation (trough implicit call the generated __init__ method).
    Consider sub-classing `Boxed` descriptor for this purpose
    and reuse its __set__ implementation, that raises `TypeError`
    if required argument was missed
    and custom descriptor subclass does not provide the default value
    either by `default` attribute or by `__get__` implementation.

    """
    fields = Field.s_from(cls)
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
                        [f'  self.{_POST_INIT_NAME}({post_init_params_str})']
                        if has_post_init
                        else []
                    ),
                ]
            )
            or '  pass',
            ' return __init__',
        ]
    )

    namespace = {}
    # pylint: disable=exec-used
    exec(wrapper_fn, None, namespace)

    init_fn = namespace['wrapper'](**locals_)

    _set_new_attribute(cls, '__init__', init_fn)

    for field in fields:
        setattr(cls, field.name, field.descriptor)

    if not getattr(cls, '__doc__'):
        cls.__doc__ = cls.__name__ + str(inspect.signature(cls)).replace(' -> None', '')

    return cls


def replace(obj, **changes):
    """Return a new object replacing specified fields with new values.

    Example:

        >>> @dataclass
        >>> class C:
        >>>     x: int
        >>>     y: int
        >>>
        >>> c = C(1, 2)
        >>> c1 = replace(c, x=3)
        >>> assert c1.x == 3 and c1.y == 2
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
            if f._field_type is dataclasses._FIELD_INITVAR and f.default is MISSING:
                raise ValueError(
                    f"InitVar {f.name!r} " 'must be specified with replace()'
                )
            changes[f.name] = getattr(obj, f.box_name)

    return obj.__class__(**changes)
