from enum import Enum
from typing import Optional

import dotenv
import pydantic

from examples.run_cross_platform_android_ios.wikipedia_app_tests.support import path


class EnvContext(Enum):
    android = 'android'
    ios = 'ios'
    # bstack_android = 'bstack_android'
    # bstack_ios = 'bstack_ios'
    # local_android = 'local_android'
    # local = 'local'
    # local_ios = 'local_ios'


class Config(pydantic.BaseSettings):
    context: EnvContext = EnvContext.android
    driver_remote_url: str = 'http://127.0.0.1:4723'

    app_package: str = 'org.wikipedia.alpha'
    app = './app-alpha-universal-release.apk'
    appWaitActivity = 'org.wikipedia.*'
    deviceName: Optional[str] = None
    bstack_userName: Optional[str] = None
    bstack_accessKey: Optional[str] = None
    platformVersion: Optional[str] = None

    @property
    def bstack_creds(self):
        return {
            'userName': self.bstack_userName,
            'accessKey': self.bstack_accessKey,
        }

    @property
    def runs_on_bstack(self):
        return self.app.startswith('bs://')

    def to_driver_options(self):
        if self.context is EnvContext.android:
            from appium.options.android import UiAutomator2Options

            options = UiAutomator2Options()

            if self.deviceName:
                options.set_capability('deviceName', self.deviceName)

            if self.appWaitActivity:
                options.set_capability('appWaitActivity', self.appWaitActivity)

            options.set_capability(
                'app',
                (
                    self.app
                    if (self.app.startswith('/') or self.runs_on_bstack)
                    else path.relative_from_root(self.app)
                ),
            )

            if self.platformVersion:
                options.set_capability('platformVersion', self.platformVersion)

            if self.runs_on_bstack:
                options.set_capability(
                    'bstack:options',
                    {
                        'projectName': 'Wikipedia App Tests',
                        'buildName': 'browserstack-build-1',  # TODO: use some unique value
                        'sessionName': 'BStack first_test',  # TODO: use some unique value
                        **self.bstack_creds,
                    },
                )

            return options
        else:
            raise ValueError(f'Unsupported context: {self.context}')


config = Config(dotenv.find_dotenv())  # type: ignore
