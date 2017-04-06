# todo: make the properties also 'object oriented' to support different configs per different SeleneDriver instances
import itertools
import os
import time

from selene.browsers import BrowserName
from selene.helpers import env


timeout = env('selene_timeout') or 4
poll_during_waits = env('selene_poll_during_waits') or 0.1

base_url = env('selene_base_url') or ''
app_host = None
# todo: we may probably refactor selene.config to selene.browser.config where config - is an object, not a module
# todo: then it would be better to add warnings.warn("use base_url instead", DeprecationWarning)

# todo: make cashing work (currently will not work...)
cash_elements = env('selene_cache_elements') == 'True' or False
'''To cash all elements after first successful find
      config.cash_elements = True'''

browser_name = env('selene_browser_name') or BrowserName.FIREFOX

start_maximized = False if env('selene_start_maximized') == 'False' else True

hold_browser_open = env('selene_hold_browser_open') == 'True' or False

counter = itertools.count(start=int(round(time.time() * 1000)))

reports_folder = env('selene_screenshot_folder') or os.path.join(os.path.expanduser('~'),
                                                                    '.selene',
                                                                    'screenshots',
                                                                 str(next(counter)))

desired_capabilities = None
