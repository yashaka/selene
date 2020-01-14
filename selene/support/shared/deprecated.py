# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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
import warnings

from selene.support.shared import config


class OldConfig:
    @property
    def timeout(self):
        warnings.warn('selene.config.timeout is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.timeout

    @timeout.setter
    def timeout(self, value):
        warnings.warn('selene.config.timeout is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.timeout = value

    @property
    def poll_during_waits(self):
        warnings.warn('selene.config.poll_during_waits is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.poll_during_waits

    @poll_during_waits.setter
    def poll_during_waits(self, value):
        warnings.warn('selene.config.poll_during_waits is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.poll_during_waits = value

    @property
    def base_url(self):
        warnings.warn('selene.config.base_url is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.base_url

    @base_url.setter
    def base_url(self, value):
        warnings.warn('selene.config.base_url is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.base_url = value

    @property
    def app_host(self):
        warnings.warn('selene.config.app_host is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.base_url

    @app_host.setter
    def app_host(self, value):
        warnings.warn('selene.config.app_host is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.base_url = value

    @property
    def cash_elements(self):
        warnings.warn('selene.config.cash_elements is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.cash_elements

    @cash_elements.setter
    def cash_elements(self, value):
        warnings.warn('selene.config.cash_elements is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.cash_elements = value

    @property
    def browser_name(self):
        warnings.warn('selene.config.browser_name is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.browser_name

    @browser_name.setter
    def browser_name(self, value):
        warnings.warn('selene.config.browser_name is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.browser_name = value

    @property
    def start_maximized(self):
        warnings.warn('selene.config.start_maximized is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.start_maximized

    @start_maximized.setter
    def start_maximized(self, value):
        warnings.warn('selene.config.start_maximized is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.start_maximized = value

    @property
    def hold_browser_open(self):
        warnings.warn('selene.config.hold_browser_open is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.hold_browser_open

    @hold_browser_open.setter
    def hold_browser_open(self, value):
        warnings.warn('selene.config.hold_browser_open is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.hold_browser_open = value

    @property
    def counter(self):
        warnings.warn('selene.config.counter is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.counter

    @counter.setter
    def counter(self, value):
        warnings.warn('selene.config.counter is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.counter = value

    @property
    def reports_folder(self):
        warnings.warn('selene.config.reports_folder is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.reports_folder

    @reports_folder.setter
    def reports_folder(self, value):
        warnings.warn('selene.config.reports_folder is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.reports_folder = value

    @property
    def desired_capabilities(self):
        warnings.warn('selene.config.desired_capabilities is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        return config.desired_capabilities

    @desired_capabilities.setter
    def desired_capabilities(self, value):
        warnings.warn('selene.config.desired_capabilities is deprecated, '
                      'use `from selene.support.shared import config` import',
                      DeprecationWarning)
        config.desired_capabilities = value
