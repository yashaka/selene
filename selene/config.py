# todo: make the properties also 'object oriented' to support different configs per different SeleneDriver instances
import itertools
import os
import time

from selene.browsers import BrowserName
from selene.environment import *
from selene.helpers import env

timeout = int(env(SELENE_TIMEOUT, 4))
poll_during_waits = float(env(SELENE_POLL_DURING_WAITS, 0.1))

base_url = env(SELENE_BASE_URL, '')
app_host = None
# todo: we may probably refactor selene.config to selene.browser.config where config - is an object, not a module
# todo: then it would be better to add warnings.warn("use base_url instead", DeprecationWarning)

# todo: make cashing work (currently will not work...)
cash_elements = env(SELENE_CACHE_ELEMENTS) == 'True' or False
'''To cash all elements after first successful find
      config.cash_elements = True'''

browser_name = env(SELENE_BROWSER_NAME, BrowserName.FIREFOX)

start_maximized = False if env(SELENE_START_MAXIMIZED) == 'False' else True

hold_browser_open = env(SELENE_HOLD_BROWSER_OPEN) == 'True' or False

counter = itertools.count(start=int(round(time.time() * 1000)))

_default_folder = os.path.join(os.path.expanduser('~'), '.selene', 'screenshots', str(next(counter)))
reports_folder = env(SELENE_REPORTS_FOLDER, _default_folder)

desired_capabilities = None
