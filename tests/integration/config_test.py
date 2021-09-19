# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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
from selene.support.shared import config
from selene import config as old_config


class TestSeleneOldConfig:
    old_timeout = old_config.timeout
    old_polling_interval = old_config.poll_during_waits
    old_base_url = old_config.base_url
    old_browser_name = old_config.browser_name
    old_hold_browser_open = old_config.hold_browser_open

    def setup_class(self):
        config.timeout = 3
        config.poll_during_waits = 0.7
        config.base_url = "http://localhost"
        config.browser_name = "firefox"
        config.hold_browser_open = True

    def teardown_class(self):
        config.timeout = self.old_timeout
        config.poll_during_waits = self.old_polling_interval
        config.base_url = self.old_base_url
        config.browser_name = self.old_browser_name
        config.hold_browser_open = self.old_hold_browser_open

    def test_timeout(self):
        assert config.timeout == 3

    def test_pooling_wait(self):
        assert config.poll_during_waits == 0.7

    def test_base_url(self):
        assert config.base_url == "http://localhost"

    def test_browser_name(self):
        assert config.browser_name == "firefox"

    def test_hold_browser_open(self):
        assert config.hold_browser_open is True


class TestSeleneSharedConfig:
    old_timeout = config.timeout
    old_polling_interval = config.poll_during_waits
    old_base_url = config.base_url
    old_browser_name = config.browser_name
    old_hold_browser_open = config.hold_browser_open

    def setup_class(self):
        config.timeout = 5
        config.poll_during_waits = 0.3
        config.base_url = "http://_localhost"
        config.browser_name = "firefox"
        config.start_maximized = True
        config.hold_browser_open = True

    def teardown_class(self):
        config.timeout = self.old_timeout
        config.poll_during_waits = self.old_polling_interval
        config.base_url = self.old_base_url
        config.browser_name = self.old_browser_name
        config.hold_browser_open = self.old_hold_browser_open

    def test_timeout(self):
        assert config.timeout == 5

    def test_pooling_wait(self):
        assert config.poll_during_waits == 0.3

    def test_base_url(self):
        assert config.base_url == "http://_localhost"

    def test_browser_name(self):
        assert config.browser_name == "firefox"

    def test_hold_browser_open(self):
        assert config.hold_browser_open is True
