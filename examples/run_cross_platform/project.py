from typing_extensions import Literal

import dotenv
import pydantic

# TODO: refactor to enum
Context = Literal[
    'bstack_android',
    # 'bstack_ios',
    # 'bstack_web',
    # 'local_android',
    # 'local_ios',
    'local_web',
    # 'selenoid_web',
]


class Config(pydantic.BaseSettings):
    context: Context = 'bstack_android'
    bstack_accessKey: str
    bstack_userName: str = 'admin'
    app_package: str = 'org.wikipedia.alpha'

    @property
    def bstack_creds(self):
        return {
            'userName': self.bstack_userName,
            'accessKey': self.bstack_accessKey,
        }


config = Config(dotenv.find_dotenv())  # type: ignore
