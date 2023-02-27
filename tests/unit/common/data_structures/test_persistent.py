from selene.common.data_structures import persistent
import typing


class Test__dataclass:
    def test_init_fucntion_was_created_and_has_the_right_types(self):
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

    def test_original_dataclasses_asdict_works(self):
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
                fields: typing.Dict[str, persistent._Field] = getattr(
                    self.__class__, persistent._FIELDS, {}
                )
                for field in fields.values():
                    if field.type_ is str:
                        setattr(
                            self, field.name, getattr(self, field.name).upper()
                        )

        pet = Pet('fido', 3, False)

        assert pet.name == 'FIDO'
        assert pet.age == 3
        assert pet.in_house is False
        assert pet.sound == 'WOOF'

    # todo: break down into atomic unit tests
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
        sub_sub_avatar_with_sub_url_n_own_timeout = (
            sub_avatar_with_own_url.with_(timeout=20.0)
        )

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new.com'
        )
        assert sub_sub_avatar_with_sub_url_n_own_timeout.timeout == 20.0
        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.browser_name == 'chrome'
        )

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
        sub_sub_avatar_with_sub_url_n_own_timeout.base_url = (
            'https://new_2.com'
        )

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new_2.com'
        )
        assert sub_avatar_with_own_url.base_url == 'https://new_2.com'
        assert sub_avatar.base_url == 'https://original.com'
        assert config.base_url == 'https://original.com'

        # WHEN
        sub_avatar_with_own_url.base_url = 'https://new_3.com'

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new_3.com'
        )
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original.com'
        assert config.base_url == 'https://original.com'

        # WHEN
        sub_avatar.base_url = 'https://original_2.com'

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new_3.com'
        )
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_2.com'
        assert config.base_url == 'https://original_2.com'

        # WHEN
        config.base_url = 'https://original_3.com'

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new_3.com'
        )
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_3.com'
        assert config.base_url == 'https://original_3.com'

        # WHEN
        config.base_url = 'https://original_3.com'

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.base_url
            == 'https://new_3.com'
        )
        assert sub_avatar_with_own_url.base_url == 'https://new_3.com'
        assert sub_avatar.base_url == 'https://original_3.com'
        assert config.base_url == 'https://original_3.com'

        # WHEN
        config.browser_name = 'firefox'

        assert (
            sub_sub_avatar_with_sub_url_n_own_timeout.browser_name == 'firefox'
        )
        assert sub_avatar_with_own_url.browser_name == 'firefox'
        assert sub_avatar.browser_name == 'firefox'
        assert config.browser_name == 'firefox'
