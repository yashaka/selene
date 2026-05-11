from enum import Enum

import dotenv
import pydantic


class Context(Enum):
    bstack_android = 'bstack_android'
    # bstack_ios = 'bstack_ios'
    # bstack_web = 'bstack_web'
    # local_android = 'local_android'
    # local_ios = 'local_ios'
    local_web = 'local_web'
    # selenoid_web = 'selenoid_web'


class Config(pydantic.BaseSettings):
    context: Context = Context.bstack_android
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
