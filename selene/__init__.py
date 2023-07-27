# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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

from . import support

from selene.core.configuration import (
    Config as _CustomConfigForCustomBrowser,
)

Config = _CustomConfigForCustomBrowser

from selene.core.entity import (
    Browser as _CustomBrowser,
)

Browser = _CustomBrowser

"""
Given::

    from selenium.webdriver import Chrome

AND chromedriver executable available in $PATH

WHEN::

    from selene import Browser, Config

    browser = Browser(Config(
        driver=Chrome(),
        base_url='https://google.com',
        timeout=2))

AND (uncomment if needed)::

    # import atexit
    # atexit.register(browser.quit)

AND::

    browser.open('/ncr')

"""

from selene import _managed  # noqa

browser = _managed.browser

from selene.support import by as _by_style_selectors  # noqa

by = _by_style_selectors
"""
AND::

    # browser.element('//*[@name="q"]')).type('selenium').press_enter()
    # OR...

    # browser.element('[name=q]')).type('selenium').press_enter()
    # OR...

    from selene import by

    # browser.element(by.name('q')).type('selenium').press_enter()
    # OR...for total readability

    query = browser.element(by.name('q'))  # actual search doesn't start here, the element is "lazy"
         # here the actual webelement is found
    query.type('selenium').press_enter()
                          # and here it's located again, i.e. the element is "dynamic"

"""

from selene.support.conditions import be as _be_style_conditions  # noqa

be = _be_style_conditions
"""
AND (in case we need to filter collection of items by some condition like visibility)::

    from selene import be

    results = browser.all('.srg .g').filtered_by(be.visible)
"""

from selene.support.conditions import have as _have_style_conditions  # noqa

have = _have_style_conditions
"""
THEN::
    from selene import have

    # results.should(have.size(10))
    # results.first.should(have.text('Selenium automates browsers'))
    # OR...

    results.should(have.size(10))\
        .first.should(have.text('Selenium automates browsers'))

FINALLY (if not registered "atexit" before)::

    browser.quit()
"""

####################
# Advanced Helpers #
####################

from selene.core import command as _advanced_commands  # noqa

command = _advanced_commands
"""
Sometimes you might need some extra actions on elements,
e.g. for workaround something through js::

    from selene import command

    browser.element('#not-in-view').perform(command.js.scroll_into_view)
"""

from selene.core import query as _advanced_queries  # noqa

query = _advanced_queries
# its = _advanced_queries  # TODO: do we really need it too? for better readability: .get(its.text)
"""
Probably you think that will need something like::

    from selene import query

    product_text = browser.element('#to-assert-something-non-standard').get(query.text)
    price = my_int_from(product_text)
    assert price > 100

But usually it's either better to implement your custom condition::

    browser.element('#to-assert-something-non-standard').should(have_in_text_the_int_number_more_than(100))

Where the ``have_in_text_the_int_number_more_than`` is your defined custom condition.
Such condition-based alternative will be less fragile,
because python's assert does not have "implicit waiting",
like selene's should ;)


Furthermore, the good test is when you totally control your test data, and instead::


    product = browser.element('#to-remember-for-future')

    product_text_before = product.get(query.text)
    price_before = my_int_from(product_text_before)

    # ... do something

    product_text_after = product.get(query.text)
    price_after = my_int_from(product_text_after)

    assert price_after > price_before


Normally, better would be to refactor to something like::

    product = browser.element('#to-remember-for-future')

    product.should(have.text('100$'))

    # ... do something

    product.should(have.text('125$'))


You might think you need something like::

    from selene import query

    if browser.element('#i-might-say-yes-or-no').get(query.text) == 'yes':
        # do something...

Or::

    from selene import query

    if browser.all('.option').get(query.size) >= 2:
        # do something...


Maybe one day, you really find a use case:) But for above cases, probably easier would be::

    if browser.element('#i-might-say-yes-or-no').wait_until(have.text('yes'):
        # do something

    # ...

    if browser.all('.i-will-appear').wait_until(have.size_greater_than_or_equal(2)):
        # do something

Or, by using non-waiting versions, if "you are in a rush:)"::

    if browser.element('#i-might-say-yes-or-no').matching(have.text('yes'):
        # do something

    # ...

    if browser.all('.i-will-appear').matching(have.size_greater_than_or_equal(2)):
        # do something

"""

# """
# Just types...
# """
from selene.core.entity import Element, Collection  # noqa

__version__ = '2.0.0rc3post2'
