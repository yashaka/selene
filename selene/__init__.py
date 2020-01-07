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

# todo: deprecate all these imports... or not?

from selene.support.shared import browser as _shared_browser_with_automatic_driver_initialization
browser = _shared_browser_with_automatic_driver_initialization


from selene.support import by as _by_style_selectors
by = _by_style_selectors


from selene.support.conditions import be as _be_style_conditions
be = _be_style_conditions


from selene.support.conditions import have as _have_style_conditions
have = _have_style_conditions


from selene.support.shared import config as _shared_config_to_customize_shared_browser_before_use
config = _shared_config_to_customize_shared_browser_before_use


from selene.entity import Browser as _custom_browser
Browser = _custom_browser


from selene.configuration import Config as _custom_config_for_custom_browser
Config = _custom_config_for_custom_browser


# todo: consider moving all selene.* modules somewhere deeper (for example into selene.core.*)
#       then import here only selene.api.base
#       maybe do this in >= 3
