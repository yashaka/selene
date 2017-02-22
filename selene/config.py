# todo: make the properties also "object oriented" to support different configs per different SeleneDriver instances
import itertools
import os
import time

from selene.browsers import Browser
from selene.helpers import env

SELENE_TIMEOUT = "selene_timeout"
SELENE_POOLING_INTERVAL = "selene_polling_interval"
SELENE_BASE_URL = 'selene_base_url'
SELENE_BROWSER = 'selene_browser'
SELENE_START_MAXIMIZED = "selene_start_maximized"
SELENE_HOLD_BROWSER_OPEN = "selene_hold_browser_open"
SELENE_CACHE_ELEMENTS = "selene_cache_elements"
SELENE_SCREENSHOT_FOLDER = "selene_screenshot_folder"

timeout = env(SELENE_TIMEOUT) or 4
poll_during_waits = env(SELENE_POOLING_INTERVAL) or 0.1
app_host = env(SELENE_BASE_URL) or ''

# todo: make cashing work (currently will not work...)
cash_elements = env(SELENE_CACHE_ELEMENTS) == "True" or False
"""To cash all elements after first successful find
      config.cash_elements = True"""

browser_name = env(SELENE_BROWSER) or Browser.FIREFOX

maximize_window = False if env(SELENE_START_MAXIMIZED) == "False" else True

hold_browser_open = env(SELENE_HOLD_BROWSER_OPEN) == "True" or False

counter = itertools.count(start=int(round(time.time() * 1000)))

screenshot_folder = env(SELENE_SCREENSHOT_FOLDER) or os.path.join(os.path.expanduser("~"),
                                                                  ".selene",
                                                                  "screenshots",
                                                                  str(next(counter)))

desired_capabilities = None
