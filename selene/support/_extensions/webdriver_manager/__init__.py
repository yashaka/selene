from . import patch

import webdriver_manager

if webdriver_manager.__version__ == '3.8.6':
    from webdriver_manager.core.utils import ChromeType as _ChromeType
else:
    from webdriver_manager.core.os_manager import ChromeType as _ChromeType

ChromeType = _ChromeType
