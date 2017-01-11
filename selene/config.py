# todo: make the properties also "object oriented" to support different configs per different SeleneDriver instances
import os

from selene.browsers import Browser

timeout = 4
poll_during_waits = 0.1
app_host = ''

# todo: make cashing work (currently will not work...)
cash_elements = False
"""To cash all elements after first successful find
      config.cash_elements = True"""

browser_name = Browser.FIREFOX
screenshot_folder = "{}/screenshots".format(os.path.expanduser("~"))
