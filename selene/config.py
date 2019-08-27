# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

browser_name = env(SELENE_BROWSER_NAME, BrowserName.CHROME)

start_maximized = False if env(SELENE_START_MAXIMIZED) == 'False' else True

hold_browser_open = env(SELENE_HOLD_BROWSER_OPEN) == 'True' or False

counter = itertools.count(start=int(round(time.time() * 1000)))

_default_folder = os.path.join(os.path.expanduser('~'), '.selene', 'screenshots', str(next(counter)))
reports_folder = env(SELENE_REPORTS_FOLDER, _default_folder)

desired_capabilities = None
