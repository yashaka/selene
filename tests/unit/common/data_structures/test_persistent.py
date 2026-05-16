import inspect
import dataclasses

from selene.common.data_structures import persistent
import typing
import pytest


# TODO: find gaps in coverage and break down tests to be more atomic
class Test__dataclass:
    def test_init_function_was_created_and_has_the_right_types(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            sound: str = 'woof'

        assert hasattr(Pet, '__init__')
        assert typing.get_type_hints(Pet.__init__) == {
            'age': int,
            'name': str,
            'sound': str,
        }

    def test_properties_are_assigned_and_the_default_works(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            sound: str = 'woof'

        fido = Pet('fido', 3)

        assert fido.name == 'fido'
        assert fido.age == 3
        assert fido.sound == 'woof'

    def test_default_can_be_overriden(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            sound: str = 'woof'

        rover = Pet('rover', 5, 'bark')

        assert rover.name == 'rover'
        assert rover.age == 5
        assert rover.sound == 'bark'

    def test_properties_can_be_reassigned(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            in_house: bool = True
            sound: str = 'woof'

        fido = Pet('fido', 3, False)

        fido.name = 'odif'
        fido.age = 6
        fido.in_house = False
        fido.sound = 'foow'

        assert fido.name == 'odif'
        assert fido.age == 6
        assert fido.in_house is False
        assert fido.sound == 'foow'

    def test_original_dataclasses_asdict_returns_unboxed_values(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            in_house: bool = True
            sound: str = 'woof'

        import dataclasses

        fido_dict = dataclasses.asdict(Pet('fido', 3, False))  # noqa WPS110

        assert fido_dict == {
            'name': 'fido',
            'age': 3,
            'in_house': False,
            'sound': 'woof',
        }

    def test_post_init_jumps_in(self):
        @persistent.dataclass
        class Pet:
            name: str
            age: int
            in_house: bool = True
            sound: str = 'woof'

            def __post_init__(self):
                fields: typing.Dict[str, persistent.Field] = getattr(
                    self.__class__, persistent._FIELDS, {}
                )
                for field in fields.values():
                    if field.type_ is str:
                        setattr(self, field.name, getattr(self, field.name).upper())

        pet = Pet('fido', 3, False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'WOOF'

    def test_boxed_descriptor_subclass_as_default_jumps_in(self):
        class AllStringsToUpperDescriptor(persistent.Boxed):
            def __get__(self, instance, owner):
                value = super().__get__(instance, owner)
                return value.upper() if isinstance(value, str) else value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = AllStringsToUpperDescriptor()
            in_house: bool = True
            sound: str = 'woof'

        # WHEN
        pet = Pet(name='fido', age=3, in_house=False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'woof'

    def test_boxed_descriptor_subclass_as_default_in_explicit_field_jumps_in(
        self,
    ):
        class AllStringsToUpperDescriptor(persistent.Boxed):
            def __get__(self, instance, owner):
                value = super().__get__(instance, owner)
                return value.upper() if isinstance(value, str) else value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = persistent.field(default=AllStringsToUpperDescriptor())
            in_house: bool = True
            sound: str = 'woof'

        # WHEN
        pet = Pet(name='fido', age=3, in_house=False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'woof'

    def test_boxed_descriptor_subclass_raises_on_missed_args(
        self,
    ):
        class AllStringsToUpperDescriptor(persistent.Boxed):
            def __get__(self, instance, owner):
                value = super().__get__(instance, owner)
                return value.upper() if isinstance(value, str) else value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = persistent.field(default=AllStringsToUpperDescriptor())

        # WHEN
        try:
            Pet(age=3)

        except TypeError as e:
            assert '__init__() missing required argument to be stored' in str(e)

    def test_boxed_descriptor_subclass_with_default_allow_to_miss_args(
        self,
    ):
        class AllStringsToUpperDescriptor(persistent.Boxed):
            def __init__(self, *, default: str):
                super().__init__()
                self.default = default

            def __get__(self, instance, owner):
                value = super().__get__(instance, owner)
                return value.upper() if isinstance(value, str) else value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = AllStringsToUpperDescriptor(default='anonymous')

        # WHEN
        pet = Pet(age=3)

        assert pet.name == 'ANONYMOUS'

    def test_boxed_descriptor_subclass_with_default_passed_in_field_allow_to_miss_args(
        self,
    ):
        class AllStringsToUpperDescriptor(persistent.Boxed):
            def __init__(self, *, default: str):
                super().__init__()
                self.default = default

            def __get__(self, instance, owner):
                value = super().__get__(instance, owner)
                return value.upper() if isinstance(value, str) else value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = persistent.field(
                default=AllStringsToUpperDescriptor(default='anonymous')
            )

        # WHEN
        pet = Pet(age=3)

        assert pet.name == 'ANONYMOUS'

    def test_custom_without_set_name_descriptor_as_default_works_and_persists(
        self,
    ):  # TODO: break this test into atomic ones
        class AllStringsToUpperDescriptor:
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                value = getattr(instance, self.name).value
                return value.upper() if isinstance(value, str) else value

            def __set__(self, instance, value):
                if not hasattr(instance, self.name):
                    if isinstance(value, persistent.Box):
                        setattr(instance, self.name, value)
                    else:
                        setattr(instance, self.name, persistent.Box(value))
                else:
                    getattr(instance, self.name).value = value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = AllStringsToUpperDescriptor()
            # name: str = AllStringsToUpperDescriptor('name')
            in_house: bool = True
            sound: str = 'woof'

        # WHEN
        pet = Pet(name='fido', age=3, in_house=False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'woof'

    def test_custom_with_set_name_and_default_descriptor_as_default_works_and_persists(
        self,
    ):  # TODO: break this test into atomic ones
        class AllStringsToUpperDescriptor:
            def __init__(self, *, default=None):
                self.default = default
                self.name = None  # will be set by persistent.dataclass logic

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                value = getattr(instance, self.name).value
                return value.upper() if isinstance(value, str) else value

            def __set__(self, instance, value):
                if not hasattr(instance, self.name):
                    if isinstance(value, persistent.Box):
                        setattr(instance, self.name, value)
                    elif inspect.isdatadescriptor(value):
                        # try to find default inside descriptor
                        default = getattr(value, 'default', None)
                        if default is not None:
                            setattr(instance, self.name, persistent.Box(default))
                            return
                        else:
                            raise ValueError(
                                f'Cannot find default value for {value.name}, '
                                f'please provide it explicitly'
                            )

                    else:
                        setattr(instance, self.name, persistent.Box(value))
                else:
                    getattr(instance, self.name).value = value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = AllStringsToUpperDescriptor()
            # name: str = AllStringsToUpperDescriptor('name')
            in_house: bool = True
            sound: str = AllStringsToUpperDescriptor(default='woof')

        # WHEN
        pet = Pet(name='fido', age=3, in_house=False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'WOOF'

        # WHEN
        clone = persistent.replace(pet, sound='foow')
        clone.name = 'odif'
        clone.age = 6
        clone.sound = 'foow!!!'

        # THEN
        assert clone.name == 'ODIF'
        assert clone.age == 6
        assert clone.in_house is False
        assert clone.sound == 'FOOW!!!'

        assert pet.name == 'ODIF'
        assert pet.age == 6
        assert pet.in_house is False
        assert pet.sound == 'WOOF'

    def test_missing_required_argument_raises_type_error_about_missed_arg(
        self,
    ):
        @persistent.dataclass
        class Pet:
            age: int
            name: str

        try:
            Pet(age=3)

        except TypeError as e:
            assert "missing 1 required positional argument: 'name'" in str(e)

    def test_custom_descriptor_as_default_in_explicit_field_works_and_persists(
        self,
    ):  # TODO: break this test into atomic ones
        class AllStringsToUpperDescriptor:
            def __init__(self):
                self.name = None

            def __set_name__(self, owner, name):
                if getattr(self, name, None) is None:
                    self.name = name

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                value = getattr(instance, self.name).value
                return value.upper() if isinstance(value, str) else value

            def __set__(self, instance, value):
                if not hasattr(instance, self.name):
                    if isinstance(value, persistent.Box):
                        setattr(instance, self.name, value)
                    else:
                        setattr(instance, self.name, persistent.Box(value))
                else:
                    getattr(instance, self.name).value = value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = persistent.field(default=AllStringsToUpperDescriptor())
            # name: str = AllStringsToUpperDescriptor('name')
            in_house: bool = True
            sound: str = 'woof'

        # WHEN
        pet = Pet(name='fido', age=3, in_house=False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'woof'

        # WHEN
        clone = persistent.replace(pet, sound='foow')
        clone.name = 'odif'
        clone.age = 6
        clone.sound = 'foow!!!'

        # THEN
        assert clone.name == 'ODIF'
        assert clone.age == 6
        assert clone.in_house is False
        assert clone.sound == 'foow!!!'

        assert pet.name == 'ODIF'
        assert pet.age == 6
        assert pet.in_house is False
        assert pet.sound == 'woof'

    def test_custom_descriptor_without_missed_args_handler_will_hide_problems(
        self,
    ):  # TODO: break this test into atomic ones
        class AllStringsToUpperDescriptor:
            def __init__(self):
                self.name = None

            def __set_name__(self, owner, name):
                if getattr(self, name, None) is None:
                    self.name = name

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                value = getattr(instance, self.name).value
                return value.upper() if isinstance(value, str) else value

            def __set__(self, instance, value):
                if not hasattr(instance, self.name):
                    if isinstance(value, persistent.Box):
                        setattr(instance, self.name, value)
                    else:
                        setattr(instance, self.name, persistent.Box(value))

                # GIVEN NO HANDLER FOR MISSED ARGS on __init__(...)

                # elif persistent._is_of_descriptor_type(value):
                #     # try to find default inside descriptor
                #     default = getattr(value, 'default', None)
                #     if default is not None:
                #         setattr(
                #             instance, self.name, persistent.Box(default)
                #         )
                #         return
                #     else:
                #         raise ValueError(
                #             f'Cannot find default value for {value.name}, '
                #             f'please provide it explicitly'
                #         )

                else:
                    getattr(instance, self.name).value = value

        @persistent.dataclass
        class Pet:
            age: int
            name: str = persistent.field(default=AllStringsToUpperDescriptor())

        # WHEN
        pet = Pet(age=3)  # no Error here :(

        assert isinstance(pet.name, AllStringsToUpperDescriptor)

    # TODO: break down into atomic unit tests
    def test_persistent_replace(self):
        @persistent.dataclass
        class Config:
            base_url: str
            timeout: float = 4.0
            browser_name: str = 'chrome'

            def with_(self, **kwargs):
                return persistent.replace(self, **kwargs)

        config = Config(base_url='https://original.com', timeout=2.0)

        # WHEN
        sub_avatar = config.with_()

        assert sub_avatar.base_url == 'https://original.com'
        assert sub_avatar.timeout == 2.0
        assert sub_avatar.browser_name == 'chrome'

        # WHEN
        sub_avatar_with_own_url = config.with_(base_url='https://new.com')

        assert sub_avatar_with_own_url.base_url == 'https://new.com'
        assert sub_avatar_with_own_url.timeout == 2.0
        assert sub_avatar_with_own_url.browser_name == 'chrome'

        # WHEN
        sub_sub_avatar_with_sub_url_n_own_timeout = sub_avatar_with_own_url.with_(
            timeout=20.0
        )

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new.com'
        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 20.0
        assert sub_sub_avatar_with_sub_url_n_own_timeout.browser_name == 'chrome'

        # WHEN
        sub_sub_avatar_with_sub_url_n_own_timeout.timeout = 21.0

        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 21.0
        assert sub_avatar_with_own_url.timeout == 2.0
        assert sub_avatar.timeout == 2.0
        assert config.timeout == 2.0

        # WHEN
        sub_avatar_with_own_url.timeout = 3.0

        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 21.0
        assert sub_avatar_with_own_url.timeout == 3.0
        assert sub_avatar.timeout == 3.0
        assert config.timeout == 3.0

        # WHEN
        sub_avatar.timeout = 4.0

        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 21.0
        assert sub_avatar_with_own_url.timeout == 4.0
        assert sub_avatar.timeout == 4.0
        assert config.timeout == 4.0

        # WHEN
        config.timeout = 5.0

        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 21.0
        assert sub_avatar_with_own_url.timeout == 5.0
        assert sub_avatar.timeout == 5.0
        assert config.timeout == 5.0

        # WHEN
        sub_sub_avatar_with_sub_url_n_own_timeout.base_url = 'https://new_2.com'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new_2.com'
        assert sub_avatar_with_own_url.base_url == 'https://new_2.com'
        assert sub_avatar.base_url == 'https://original.com'
        assert config.base_url == 'https://original.com'

        # WHEN
        sub_avatar_with_own_url.base_url = 'https://new_3.com'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new_3.com'
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original.com'
        assert config.base_url == 'https://original.com'

        # WHEN
        sub_avatar.base_url = 'https://original_2.com'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new_3.com'
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_2.com'
        assert config.base_url == 'https://original_2.com'

        # WHEN
        config.base_url = 'https://original_3.com'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new_3.com'
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_3.com'
        assert config.base_url == 'https://original_3.com'

        # WHEN
        config.base_url = 'https://original_3.com'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.base_url == 'https://new_3.com'
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_3.com'
        assert config.base_url == 'https://original_3.com'

        # WHEN
        config.browser_name = 'firefox'

        assert sub_sub_avatar_with_sub_url_n_own_timeout.browser_name == 'firefox'
        assert sub_avatar_with_own_url.browser_name == 'firefox'
        assert sub_avatar.browser_name == 'firefox'
        assert config.browser_name == 'firefox'


class Test__persistent_internal_branches:
    def test_set_new_attribute_returns_true_if_exists(self):
        class Sample:
            already = 1

        assert persistent._set_new_attribute(Sample, 'already', 2) is True
        assert Sample.already == 1

    def test_boxed_descriptor_with_falsy_get_default_raises_type_error(self):
        class FalsyDefaultDescriptor:
            name = 'field'

            def __get__(self, instance, owner):
                return ''

            def __set__(self, instance, value):
                return None

        boxed = persistent.Boxed('field')

        class Holder:
            pass

        holder = Holder()
        with pytest.raises(TypeError):
            boxed.__set__(holder, FalsyDefaultDescriptor())

    def test_boxed_descriptor_uses_truthy_default_from_get(self):
        class TruthyDefaultDescriptor:
            name = 'field'

            def __get__(self, instance, owner):
                return 'anonymous'

            def __set__(self, instance, value):
                return None

        boxed = persistent.Boxed('field')

        class Holder:
            pass

        holder = Holder()
        boxed.__set__(holder, TruthyDefaultDescriptor())

        assert holder.field.value == 'anonymous'

    def test_field_validates_mutable_defaults_and_set_name_without_default_set_name(
        self,
    ):
        with pytest.raises(ValueError, match="Don't use mutable type"):
            persistent.Field('items', list, [])

        field = persistent.Field('', int, 1)

        class Owner:
            pass

        field.__set_name__(Owner, 'age')
        assert field.name == 'age'

    def test_field_value_from_reads_boxed_value(self):
        class Holder:
            pass

        holder = Holder()
        setattr(holder, persistent.Field.box_mask('size'), persistent.Box(42))
        assert persistent.Field.value_from(holder, 'size') == 42

    def test_replace_raises_on_non_dataclass_instance(self):
        class NotDataclass:
            pass

        with pytest.raises(
            TypeError, match='replace\\(\\) should be called on dataclass instances'
        ):
            persistent.replace(NotDataclass(), value=1)

    def test_replace_skips_classvar_field(self):
        class FakeDataclass:
            __dataclass_fields__ = {}

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeField:
            def __init__(self):
                self._field_type = dataclasses._FIELD_CLASSVAR
                self.init = True
                self.name = 'cv'
                self.default = persistent.MISSING
                self.box_name = persistent.Field.box_mask('cv')

        FakeDataclass.__dataclass_fields__ = {'cv': FakeField()}
        obj = FakeDataclass()
        result = persistent.replace(obj)
        assert isinstance(result, FakeDataclass)
        assert result.kwargs == {}

    def test_replace_init_false_field_raises_and_skip_branch(self):
        class FakeDataclass:
            __dataclass_fields__ = {}

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeField:
            def __init__(self, name):
                self._field_type = dataclasses._FIELD
                self.init = False
                self.name = name
                self.default = persistent.MISSING
                self.box_name = persistent.Field.box_mask(name)

        field = FakeField('x')
        FakeDataclass.__dataclass_fields__ = {'x': field}
        obj = FakeDataclass()

        with pytest.raises(ValueError, match='init=False'):
            persistent.replace(obj, x=1)

        result = persistent.replace(obj)
        assert result.kwargs == {}

    def test_replace_requires_initvar_without_default(self):
        class FakeDataclass:
            __dataclass_fields__ = {}

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeField:
            def __init__(self):
                self._field_type = dataclasses._FIELD_INITVAR
                self.init = True
                self.name = 'required_initvar'
                self.default = persistent.MISSING
                self.box_name = persistent.Field.box_mask(self.name)

        FakeDataclass.__dataclass_fields__ = {'required_initvar': FakeField()}
        obj = FakeDataclass()

        with pytest.raises(ValueError, match='must be specified with replace'):
            persistent.replace(obj)
