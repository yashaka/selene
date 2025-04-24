from selene import have, be
from selene.support.shared import browser

browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

# Open the Google homepage
browser.open('/ncr')

# Search for something (example)
browser.element('[name="q"]').should(be.blank).type('selene python').press_enter()
browser.all('#search .g').should(have.size_greater_than(1))

# Close the browser
browser.close()
