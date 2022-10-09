"""
todo:
- not covered
  - custom driver is kept during session
    i.e. next test module will reuse browser from previous
    if not closed there
    do we even need to cover it with test?
  - should we automatically close custom driver set by user
    when session ends and browser.config.hold_browser_open = False
    (currently we schedule automatic closure only for drivers spawned by selene)
"""

# TODO: make these tests to live inside one py module with different test classes
