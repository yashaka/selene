# Changelog

## next
- consider adding config.quit_user_driver_on_exit (maybe even True by default, maybe not...)
- case insensitive versions of conditions like have.attribute(...).value(...)
  - experimental impl was already added in 2.0.0a16
- consider making have.size to work with elements too...
- maybe somewhen in 3.0 consider adding selene.support.shared.selenide module
  - with selenide style api
    - like s, ss, open_url
    - SelenideElement#find, #find_all
    - ElementsCollection#find, #filter, #get
    - etc.
- what about ActionChains?
  - with retries?
- what about soft assertions in selene?
- improve stacktraces
  - consider using something like `__tracebackhide__ = True`
- consider adding more readable alias to by tuple, like in:
  `css_or_xpath_or_by: Union[str, tuple]`
- what about `element('#go-forward').with_(retry = (times=2, dismiss_element='#confirm')).click()`?
  - and even `browser.element('#loading-bar').with(condition=lambda: element('#loading-bar').matching(be.visible)).should(be.hidden)`
    - or even browser.when.element('#loading-bar', matching=be.visible).then.element('#loading-bar').should(be.hidden)
    - how in such case the '#loading-bar' can be reused as element?
  - other ideas
    - custom action condition
      - element('#can-be-not-ready').when.click().then.element('#some-new-element').should(be.visible)
      - element('#can-be-not-ready').with_(hook_wait=lambda: be.visible(element('#some-new-element))).click()
- improve error messages
  - should we come back to the "actual vs expected" style in error messages?
  
## 2.0.1
- add hooks
- refine API  
  - remove deprecated things

## 2.0.0b1 (to be released on??.??.2020)
- remove all deprecated things and stay calm:)
- or maybe remove all deprecated stuff only in 3.0?

## 2.0.0aNEXT (to be released on ??.??.2020)
- config.browser_name -> config.name was bad idea
  - but config.executor accepting both 'chrome'/'firefox' or 'http://<remoteurl>'
    - might be a good idea... think on it... 
- DOING: update docs
- GIVEN some.should(be.visible) and another.with_(timeout=2).should(be.visible)
  AND some test fixture logging last_screenshot from shared.config.last_screenshot
  WHEN some failed THEN the logging will work
  WHEN another failed THEN the logging will log nothing, 
    BECAUSE another has it's own config with its own last_screenshot source
    
  - todo: fix?
- todo consider adding element.caching as lazy version of element.cached
- consider adding hold_browser_opened_on_failure
- consider browser.open() over browser.open('') (use some smart defaults)
- consider cofig.headless = False like in selenide 
  - `this.browser = new Browser(config.browser(), config.headless());`
  
## 2.0.0a2x+1 (to be released on ?.??.2020)
- todo: add something like element.click_with_offset
- todo: add something like browser.perform(switch_to_tab('my tab title'))
  - maybe make browser.switch ... to work with retry logic
    or make separate command.switch...
- ensure we can't element.type on invisible element; add test for that
- use __all__ in selene api imports, etc
  - The variable __all__ is a list of public objects of that module, as interpreted by import *. ... In other words, __all__ is a list of strings defining what symbols in a module will be exported when from <module> import * is used on the module

  
## 2.0.0a2x (to be released on ?.08.2020)
- todo: improve for other all.* methods (in addition to improved errors from browser.all.element_by)
- todo: why in the past we had when outer_html this: '<button class="destroy" type="submit" displayed:false></button>'
  - but now we have this: '<button class="destroy" type="submit"></button>'?
    - can we improve it?
- add browser.all('.item').last?
- make browser.switch_to.frame to accept element
- deprecate be.present
- repeat fix of #225 to other options in shared config, refactor it... 
  - should we make original config (not shared) mutable?

## 2.0.0a36 (to be released on 30.03.2021)
- Moved selene from Pipenv to [Poetry](https://python-poetry.org/) as a greater python dependency resolver of 2021 (see #302).
- Moved to a new release process with Poetry: added bash aliases in `./.run/*.sh` (see #304).
- Moved from setup.py and setup.cfg to pyproject.toml config-file.
- Updated README.md "Release process".
- Updated CONTRIBUTING.md with `black` and `pylint` job description.

## 2.0.0a35 (released on 27.03.2021)
- added command.js.click
- if you set driver for shared.browser manually via `browser.config.driver = ...`
  now it will automatically close previous driver, if it is alive
- in selene 1.0 if you could do mixed driver management, 
  like: use automatic driver, then manual, then automatic...
  in selene 2.0 this behaviour was broken, and this version fixes this;)
- deprecated shared.config.quit_driver; use shared.config.reset_driver instead
  - actually, you don't need this method,
    in most cases you just need shared.browser.quit() – use it if you don't know what you do;)
- fixed `browser.switch_to_tab(index_or_name)` when arg is of `int` type    
    
## 2.0.0a34 (released on 22.12.2020)
- fixed [#231](https://github.com/yashaka/selene/issues/225): Need additional option to turn off logging outerHTML
  - added support.shared.config.log_outer_html_on_failure (`False` by default)

## 2.0.0a33 (released on 10.09.2020)
- fixed [#225](https://github.com/yashaka/selene/issues/225): Failed to get last_screenshot from shared browser if element with custom config failed

## 2.0.0a32 (released on 10.09.2020)
- broken release:)

## 2.0.0a31 (released on 31.07.2020)
- fixed type hints in `*.should(here)`
  - latest PyCharm 2020.2 revealed the hidden issue with typing

## 2.0.0a30 (released on 30.07.2020)
- fixed selene.support.shared.browser.with_
  - to return sharedbrowser instance instead of browser instance
- made browser.config.hold_browser_open to influence browser quit logic 
  - even if set after calling browser.open or resetting browser.config.driver

## 2.0.0a29 (released on 30.07.2020)
- fixed shared browser automatic quit on process exit
  - that led to session error 
    in case you quit shared browser manually in your fixture

## 2.0.0a28 (released on 21.05.2020)
- added support of xpath to start with `(` in `s(selector)`, etc.
  - example: `ss('(//h1|//h2)[contains(text(), "foo")]').should(have.size(10))`

## 2.0.0a27 (released on 19.05.2020)
- fixed command.js.type and configuration.type_by_js + element.type

## 2.0.0a26 (released on 19.05.2020)
- if driver was set like `shared.config.driver = my_custom_driver`
  - then it's not mandatory to call `shared.browser.open` first
    
## 2.0.0a25 (released on 18.05.2020)
- fixing [#172](https://github.com/yashaka/selene/issues/172)
  - added `shared.config.set_driver: callable[[], webdriver]`
    as alternative to `shared.config.driver: webdriver`
    - now if config.set_driver is set - it will be used 
      to create and reload the driver instance according to your needs
    - setting `shared.config.driver = my_driver` is equivalent to setting 
      then `shared.config.set_driver = lambda: my_driver`
    - only `shared.browser.open(url)` now makes `set_driver` 
      to be triggered on first start and if driver was crashed or quit
      - i.e. if driver is crashed
        any further action on `shared.browser.element` will crash too
        unless you call `shared.browser.open` again
        - browser.open will also crash 
          if you used `shared.config.driver = my_driver` before
- **removed** implementation of "re-creating browser" if shared.config.browser_name was changed
  - this should make shared.browser more friendly with appium
  - and nevertheless shared.config should be used only "after quit and before open"... 
      
    
## 2.0.0a24 (to be released on 17.05.2020)
- fixed [#210](https://github.com/yashaka/selene/issues/210)
  - when installing using pip -- unicodedecodeerror: 'charmap' codec can't decode byte
  
## 2.0.0a23 (released on 15.04.2020)

- fixed element.cached to not fail on non-existing element

- fixed conditions that "compare lists" (like "have.exact_texts")
  - failed earlier if one collection (expected or actual) was empty

- added logging of webelement outer html to the error message of failed waiting for element
  - if actually webelement was found, but something was wrong with it (like hidden or non-interactable)
  
- improved errors from browser.all.element_by
  - todo: improve for other all.* methods

was:

```
timed out after 4s, while waiting for:
browser.all(('css selector', '#task-list>li')).element_by(has exact text a).double click
reason: assertionerror: cannot find element by condition «has exact text a» from webelements collection:
[[]]
```

now:

```
timed out after 4s, while waiting for:
browser.all(('css selector', '#task-list>li')).element_by(has exact text a).double click

reason: assertionerror: 
	cannot find element by condition «has exact text a» 
	among browser.all(('css selector', '#task-list>li'))
	actual webelements collection:
	[]
```

  
## 2.0.0a22 (released on 20.03.2020)

- fixed [#206 – "after manually quitting, setting a new driver fails"](https://github.com/yashaka/selene/issues/206)
- fixed `have.texts` when actual collection has bigger size than actual
- added (yet marked with "experimental" warning)
  - `element_by_its`
  - `filtered_by_their`
  - ... see code examples below:

```
# given
#
#    .result
#        .result-title
#        .result-url
#        .result-snippet

# in addition to

results = browser.all('.result')
results.element_by(lambda result: have.text('browser tests in python')(
                          result.element('.result-title')))\
    .element('.result-url').click()

# you can now write:
results.element_by_its('.result-title', have.text('browser tests in python'))
    .element('.result-url').click()

# results.filtered_by_their('.result-title', have.text('python'))
    .should(have.size(...))

# or even
class result:
    def __init__(self, element):
        self.element = element
        self.title = self.element.element('.result-title')
        self.url = self.element.element('.result-url')

result(results.element_by_its(lambda it: result(it).title, have.text('browser tests in python')))\
    .url.click()

# it's yet marked as experimental because probably it would be enough
# to make it possible to accept callable[[element], bool] in element_by to allow:

results.element_by(
    lambda it: it.element('.result-title').matching(have.text('browser tests in python')))
    .element('.result-url').click()

# moreover... if failed, the error becomes weird if using lambdas:

# timed out after 4s, while waiting for:
# browser.all(('css selector', '.result')).element_by(<function collection.element_by_its.<locals>.<lambda> at 0x10df67f28>).element(('css selector', '.result-url')).click
# reason: assertionerror: cannot find element by condition «<function collection.element_by_its.<locals>.<lambda> at 0x10df67f28>» from webelements collection:

```
  -  
## 2.0.0a21 (released on 22.01.2020)
- fixed hooks for entities created via entity.with_(Config(...))

## 2.0.0a20 (released on 21.01.2020)
- Fixed UnicodeEncodeError: 'charmap' codec
  - thanks to [PR-197](https://github.com/yashaka/selene/pull/197) from @ak40u

## 2.0.0a19 (released on 16.01.2020)
- removed deprecation from shared.config.counter and reports_folder
- removed backports.functools-lru-cache from project dependencies
- removed six from explicit project dependencies
- removed selene.version.py (moved version number to selene.__init__.__version__)
- deprecated: by.be_following_sibling, be_parent, be_first_child
  - use xpath explicitly to not hide complexity in workaround
  - yet you can create you own xpath helpers to to show that you are using xpath but in a more readable style
    - like: x.following_sibling, ...
  - the only exception is by.text
    - it uses xpath under the hood, but so complicated that no way to use it explicitly :)
- removed warning from `collection.first`
  - it's nevertheless useless. 
  - `first` is the one of things that breaks your code when migrating to 2.*
    - after migration, just find&replace every `.first()` to `.first`, and that's it:)
    

## 2.0.0a18 (released on 14.01.2020)
- deprecated finally `send_keys`, added `press(*keys)` instead
  - use `type` for 'typing text', use `press` or `press_enter` & co for 'pressing keys' 
- removed s, ss from selene.support.shared (were added by mistake in a17)
  - yet unsure... maybe it was a good idea... to keep s, ss in shared.__init__.py too... let's think on this more...
- removed selene.api.base and selene.api.shared from distribution
  - even selene.api is not needed anymore... let's not use it... 
  - it was needed in the past for * style imports, 
    - but nevertheless it's a bad practice to do so... 
- updated readme and project long description for pypy

## 2.0.0a17 (released on 14.01.2020)
- deprecated selene.config, use `from selene.support.shared import config` instead
  - where you also can find shared browser: `from selene.support.shared import browser, config`
  - you also can go the minimalistic way with the only `browser` import:
    - `from selene.support.shared import browser`
    - `browser.config.browser_name = 'firefox'`
    - `browser.config.base_url= 'https://google.com'`
    - `browser.config.timeout = 2`
    - `browser.open('/ncr/')`
- deprecated selene.support.jquery_style_selectors
  - because it's technically is based on selene.support.shared.*, so was structured incorrectly
  - use selene.support.shared.jquery_style instead
- separate core from shared selene api in selene.*
  - now to get shared browser or config you have to import them explicitly from selene.support.shared
  - added some base docs into selene.__init__ 

## 2.0.0a16 (released on 13.01.2020)
- fixed absent screenshots for customized elements through with_
  - e.g. in `browser.element(...).with_(timeout=...).should(be.visible)`
  - as impl: moved main auto-saving screens/page_source logic to SharedConfig
  - deprecated latest_* methods in Browser in favour of last_*
- added experimental syntax for ignore_case in:
  - `browser.element(...).should(have.attribute('foo').value('bar', ignore_case=True)`
  - `browser.element(...).should(have.attribute('foo').value_containing('bar', ignore_case=True)`
  - open points:
    - while it's more or less ok here... but is it ok in:
      - `browser.all(...).should(have.texts('a', 'b', 'c', ignore_case=True')`
      - or better?
      - `browser.element(...).should(have.texts_ignoring_case('a', 'b', 'c')`
      - taking into account that one day there might be an ask for:
        - `browser.all(...).should(have.texts('a', 'b', 'c', in_any_order=True)`
        - or
        - `browser.all(...).should(have.texts_in_any_order('a', 'b', 'c')`
        - seems like better to have options over predefined names... to combine them whatever you like
          - but what then to do with conditions like value_containing? move _containing to option to?
            - `browser.element(...).should(have.value('a', contained=True, ignore_case=True')`
            - ooo, and this is also technically possible:
              - `browser.element(...).should(have.value('a').contained.ignoring_case)`

## 2.0.0a15 (released on 13.01.2020)
- fixed len(collection) to wait if collection can't be found
- made query.size to work with both element and collection
  - element.get(query.size) will return the size of the element (as a Dict)
  - collection.get(query.size) will return the size of collection (as int)
- added shared config.save_screenshot_on_failure (True by default)
- added shared config.save_page_source_on_failure (True by default)
- refactored and hardened behaviour of shared config
  - refactored waiting (moved base wait impl for entities to config.wait(entity)

## 2.0.0a14 (released on 10.01.2020)
- removed deprecation from shared.browser.save_screenshot, save_page_source, latest_screenshot, latest_page_source
  - since they nevertheless are used internally by selene
  - and methods looks like better named than original selenium ones, like `get_screenshot_as_png` :)
- refactored hooks to the style: `config.hook_wait_failure = lambda e: e`
  - the hook should be a function that receives failure as argument, 
  - process it, and return back potentially new failure object
  - by default it's just an "identity" function, returning itself
    - for shared config the default is overwritten by hook adding screenshot and page_source to the failure message
    - to disable default screenshot and page_source on failure
      - just do `config.hook_wait_failure = None`
        - yet, we may add in future explicit things like `config.screenshot_on_failure = False # True by default`
  - no other hooks avaialbe so far... somewhen in future we will add more hooks, 
    - like `config.hook_wait_command`, etc.
- fixed original `collection.all` and `collection.map` implementations (were broken in previous versions)
- marked `collection.all` with FutureWarning (yet unclear what naming would be best)
- renamed `collection.map` to `collection.all_first`, marked it as FutureWarning (yet unclear what naming would be best)
- added collection.collected(finder)
  - as a more low level, and more universal approach over collection.all and collection.all_first/map
    - given books = browser.all('.books')
    - then
    - `books.all('.author) == books.collected(lambda book: book.all('.author'))`
      - reflects all authors of all books
    - `books.all_first('.author) == books.collected(lambda book: book.element('.author'))`
      - reflects only first authors of all books
      - pay attention... all_first is not same as all(...).first:
        - `books.all('.author).first != books.all_first('.author)`
        - `books.all('.author).first == books.collected(lambda book: book.all('.author')).first`
        - `books.all('.author).first == books.first.element('.author')`
          - i.e. reflecting only the first author of the first book
- switched in wait from webdriver TimeoutException to selene.core.exceptions.TimeoutException
  - actually no need to reuse webdriver one
  - and this might help with reporting selene failure in allure reports, let's see...
- tried to implement something special for configuring remote driver management in shared config... 
  - but... just left some comments for future... 
  - it's too complicated to be implemennted in a consistent way in selene. 
  - so far the main strategy is just to create an instance on your own 
  - and then set it in config by `config.driver = webdriver.Remote(...)`, KISS ;)

## 2.0.0a13 (released on 10.01.2020)
- added temporary Collection#filter_by as deprecated 
- added temporary Collection#find_by as deprecated 
- fixed shared browser.latest_screenshot (and added browser.latest_page_source)
  - made it as property (as method it will still work as deprecated)
    - actually if you `from selene import browser` 
    - you will get deprecated browser module with latest_screenshot as method
    - the warning then will tell you to use import `from selene.support.shared import browser`
    - which will have it as a property

## 2.0.0a12 (released on 09.01.2020)
- fixed [#195](https://github.com/yashaka/selene/issues/195): added len(collection)

## 2.0.0a11 (released on 08.01.2020)
- added logging screenshot and page source hooks for failures of any waiting in shared browser behaviour
  - this is enabled by default, no option in config.* to disable such behaviour
  - yet you can turn it off by `config.hooks = Hooks(wait=WaitHooks(failure=lambda e: e)`
    - but the style/syntax of setting hooks is not completely defined, it may change in future...
- removed  SyntaxWarning for element.s and element.ss

## 2.0.0a10 (released on 08.01.2020)
- enhanced migratability
  - added syntax warning to collection.first with a hint 
    - to use .first as a property over .first() as a method
  - added selene.wait.py with wait_for alias (deprecated)
- moved all new modules from selene to selene.core
  - old deprecated modules will be removed in beta
- tuned imports to be cleaner
  - try to import everything `from selene import ...`
    - the main things you might need are: browser, config, by, be, have, Browser, Config
      - yet browser here, is old deprecated selene.browser module... 
      - so temporary import browser from selene.support.shared 
        - later once selene.browser.py is removed, you can import new browser object from selene too
    - only s and ss you will not find there, 
      - but you can import them from selene.support.jquery_style_selectors as in 1.*
- changed DeprecationWarning to SyntaxWarning for element.s and element.ss

## 2.0.0a9 (released on 07.01.2020)
- enhanced migratability of 2.*:
  - temporally added deprecated modules
    - selene.elements
    - selene.browsers
    - selene.driver
  - ensured proper config can be imported from selene (`from selene import config`)
- ensured everything potentially needed in real use is available after `from selene.api import *`
  - it includes mentioned below selene.api.base.* and selene.api.shared.* imports
- added selene.api.base for "hardcore" users
  - with `from selene.api.base import *`
  - included only Browser + Config for manual driver creation
  - and by, be, have for extra selectors and conditions
- added selene.api.shared for "easy tests with selene" with automatic driver creation
  - with `from selene.api.shared import *`
  - you can get browser.* and config.* for automatically created driver, 
    - with customization through config.*
- added also all usually needed imports to selene.*
- yet unsure what imports will be left in the end :) thinking...

## 2.0.0a8 (released on 06.01.2020)
- fixed config.* setters (timeout, base_url, etc...)

## 2.0.0a7 (released on 05.01.2020)
- removed some deprecation markings
  - from selene.common.helpers warn helpers
  - from selene.condition.not_, selene.condition.Condition#not_
  - from be.clickable

## 2.0.0a6 (released on 05.01.2020)
- fixed `entity.with_(...)`
  - where entity = browser | element | collection

## 2.0.0a5 (released on 03.01.2020)
- enhanced migratability of 2.*:
    - reflected all "old and redundant" SeleneElement methods as deprecated in Element
      - added corresponding conditions
    - reflected all "old and redundant" SeleneCollection methods as deprecated in Collection
      - did not add methods that were already deprecated in 1.*
    - temporally added selene.browser module to reflect browser.* methods from 1.* as deprecated
    - moved jquery_style_selectors.py module back to selene.support
- fixed autocomplete for *.should methods
- fixed browser.switch_to
- added `entity.with_(timeout=6)` style in addition to `entity.with_(Config(timeout=6))`
  - where entity = browser | element | collection

### known issues:
- entity.with_ does not work in case of shared browser :(
  - where entity = browser | element | collection


## 2.0.0a4 (released on 30.12.2019)
- fixed default browser_name handling in shared config; implemented some old opts in config

## 2.0.0a3 (released on 30.12.2019)
- removed from selene.support.past all not used old implementations
- tuned selene.__init__ imports to have browser (reimported from selene.support.shared)
- fixed extra modules in build for publishing
- removed six from dependencies in setup.py

## 2.0.0a2 (released on 30.12.2019)
- fixed packages to be published

## 2.0.0a1 (released on 28.12.2019, broken:))
- complete reincarnation of Selene for python version >= 3.7 :). Current limitations:
  - no test coverage; 
  - do updated docs
    - you can check the only one working test at `tests/acceptance/shared_browser/straightforward_style_test.py`
    - and use it as a fast intro 
    - keep in mind that it describes old style + new style; 
    - so you will not see there some guides for newer style; wait for that;)
  - no hooks (and so no screenshots in error messages); 
  - no temporal support for 1.0.0 aliases for some methods
    - will be added as deprecated and kept for some time to allow smoother migration

  - old implementation of everything still exists in `selene.support.past.*`
  
## 1.0.1 (released on 28.12.2019)
- no changes; just releasing latest version (before refactoring) as stable

## 1.0.0ax (next from master branch)
- removed
  - tbd
- defaults changes:
  - tbd
- naming changes:
  - tbd
- removed deprecated things: 
  - tbd
- deprecated (will produce `DeprecationWarning`):
  - tbd
- marked as "considering to deprecate" (will produce `FutureWarning`):
  - tbd
- new features:
  - tbd
  
## 1.0.0a16
- new features:
  - added `SeleneElement#matching(condition)` and `SeleneCollection#matching(condition)` 
    - as "non-waiting-predicate" version of should
    - e.g. to be used like 
        - `browser.element('#foo').matching(be.visible)` 
        - over 
        - `browser.element('#foo').is_displayed()`
          - this version will be deprecated in next versions...
- fixed `not_` usage in `SeleneCollection#element_by/filtered_by`

## 1.0.0a15
- new features:
  - added `by.id`
  - now `browser.element` can parse xpath in string selector passed as parameter

## 1.0.0a14
- removed
  - ConditionMismatchException.message (use `str(exOfConditionMismatchExceptionType)` for the same purpose)
- defaults changes:
  - changed default `browser_name` to `BrowserName.CHROME`
- added
  - `have.size_greater_than_or_equal` alias for `have.size_at_least`
  - `element.type` alias for `element.send_keys`
  - `be`, `by`, and `have` imports to `selene` module

## 1.0.0a12-13
- naming changes:
  - tbd
- removed deprecated things: 
  - `selene.tools` (use `selene.browser` instead)
  - `SeleneElement#`
    - `insist` (use `should` instead)
    - `insist_not` (use `should_not` instead)
  - `SeleneCollection#`
    - `insist` (use `should` instead)
    - `insist_not` (use `should_not` instead)
    - `filterBy` (use `filtered_by` instead)
    - `findBy` (use `element_by` instead)
    - `find` (use `element_by` instead)
- deprecated (will produce `DeprecationWarning`):
  - `SeleneCollection#`
    - `filtered` (use `filtered_by` instead)
    - `ss` (use `filtered_by` instead)
    - `s` (use `element_by` instead)
- marked as "considering to deprecate" (will produce `FutureWarning`):
  - `SeleneCollection#`
    - `filter` (consider using `filtered_by` instead)
    - `filter_by` (consider using `filtered_by` instead)
    - `find_by` (consider using `element_by` instead)
- new features:
  - [#15](https://github.com/yashaka/selene/issues/15): added `browser.title()` shortcut for `browser.driver().title`
    
## 1.0.0a11 (to be released 13.05.2017)
  - naming changes:
    - browser.visit() renamed to browser.open_url()
    - config.maximize_windows -> config.start_maximized
    - config.screenshot_folder -> config.reports_folder
  - improvements
    - screenshot link is now clickable in console output
  - bug fixes:
    - [#124](https://github.com/yashaka/selene/issues/124): If by.xpath contains utf8 symbols and not condition get UnicodeEncodeError: 'ascii'   
  - planned to remove in next version:
    - selene.tools
 
## 1.0.0a10 (released 01.03.2017)
  - [#103](https://github.com/yashaka/selene/issues/103): NEW API entry points
    - now all main selene API is available via single wildcard import: `from selene.api import *`
      - you can use the "old direct imports way" but at least until 1.0 release "the new way" will result in more stable API. We may move modules between packages, but your new way imports remain stable. See more explantains in issue description #103   
    - read Quick Start section in README.MD for more details.
  - **UPCOMING BREAKING CHANGES**:
    - deprecated selene.config.app_host, use `selene.config.base_url` instead 
      - selene.config.app_host still works but will be removed in next versions
    - [#101](https://github.com/yashaka/selene/issues/101): deprecated selene.tools, use selene.browser and selene.support.jquery_style_selectors instead or just the "new way imports from #103"
  - new features
    - [#51](https://github.com/yashaka/selene/issues/51): added ability to configure selene via passing/setting system variables
    
## 1.0.0a9 (to be released 01.03.2017)
  - skipped:)

## 1.0.0a8 (released 16.02.2017)
  - new features added
    - #76: config.maximize_window (set to True by default)
    - #68: config.hold_browser_open (set to False by default)
    - #78: config.desired_capabilities (set to None by default)
    - #92: selene.tools.latest_screenshot() (returns NoneObject if no screenshot have been added yet)
    - #85: SeleneElement#context_click()
    - #77: SeleneElement#scroll_to() (not needed in all cases, but may be usefull in some browsers sometimes...)
    - #75: support for phantomjs browser
    - conditions: url, url_containing, title_containing
    - refactored aliases implementation from selene.support.conditions.have
      - now they are implemented as method definitions giving better hints during autocomplete
  - project infrastracture
    - #84: improved travis job: added archiving build artifacts (test results)
  
## 1.0.0a7 (released 22.01.2017)
  - fixed #71: weird paths of screenshots for windows
  - updated #56: now selene should work with python 3 (but feature is not fully tested)
    
## 1.0.0a6 (released 17.01.2017)
  - added selene.tools.wait_to to wait for driver conditions like have.title, have.js_returned_true
  - added Title and JsReturnedTrue webdriver conditions
  - added selene.tools.execute_script
    
## 1.0.0a5 (released 16.01.2017)
  - refactored conditions implementation
  - broken support for python 3 (will be fixed in next versions)

## 1.0.0a4 (next from master branch)
  - added automatic screenshots on failed "should" methods
    - by default screenshots are created in {user_home}/.selene/screenshots/{id_of_current_tests_run}
    - by default the "previous run" screenshots are not cleared on "next run"
  - screenshot can be created manually by `selene.tools.take_screenshot`

## 1.0.0a3 (next from master branch)
  - improvements:
    - error messages are cleaner
      - todo: still lacks proper test coverage of all cases...
  - internal
    - refactored wait_for implementation, made it cleaner
      - todo: still need to refactor condition implementation
    
## 1.0.0a2 (not published, available via direct install from sources)
- new features:
  - automatic driver management (thanks to PR from @SergeyPirogov)
    - no more need to `set_driver`, 
      just use any command from `selene.tools`, 
      like `visit`, `s`, or `ss` and driver will be opened automatically,
      and then closed automatically (unless you decide to set it manually via `set_driver`)
    - includes automatic installation of needed drivers via [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager)
    
## 1.0.0a1 (not published, available via direct install from sources)
- internal
  - improved test coverage
    - added "given-helpers" for preconditions for atomic tests
  - completely refactored implementation to be more structural and solid
    - on the way found non-stable behavior of old implementation and fixed it
- new features:
  - object oriented paradigm is now supported in context of webdriver usage
    - Don't like "static" s, ss helpers (from selene.tools module) using global driver instance set by set_driver(...)?
    - now you can use driver.element, driver.all correspondingly
        - where driver = SeleneDriver.wrap(FirefoxDriver()), etc.
        - SeleneDriver has almost the same interface as WebDriver, but with additional methods
          - so you can do everything you can do with raw selenium when needed
  - additional "helpers" from selene.support package
    - more readable and convenient API to retrieve conditions via selene.support.(be|have)
      - e.g. `s('#element').should(have.text('foo'))`
    - more readable and convenient API to retrieve by locators via selene.support.by
      - e.g. 
        - `s(by.text('foo')).click()`
        - `s('#element').element(by.be_following_sibling).click()`
    - SeleneElement relative search shortcut-methods:
      - `s('#element').parent_element.click()`
      - `s('#element').following_sibling.click()`
      - `s('#element').first_child.click()`
- breaking changes:
  - removed out of the box but overcomplicated Widgets support via extending SElement
    - you still can create reusable Widgets in much simpler way
      - see more explanation in [#17](https://github.com/yashaka/selene/issues/17)
  - removed access by config.driver to the driver instance that was set by set_driver(...) from selene.tools
    - it's mandatory to use get_driver(...) from selene.tools for this

## 0.0.8 (released 08.12.2016)
- locked the selenium version to 2.53.1
- fixed encoding issues when working with text of elements in conditions
- added bys.by_name

## 0.0.7 (released 01.03.2016)
- fixed python3 support
- fixed the is_displayed method - now it contains implicit wait for "exist in DOM" instead of "visible"
- added ss(".element", of=Task) syntax in addition to ss(".element").of(Task)
- removed "general interceptor of all unknown methods" SElement's base class (actually commented it in code:)
- refactored lazy inner collection classes to use extend in __init__ and not use SElementsCollectionWrapper (removed the latter and SElementWrapper)
- refactored: removed unnecessary extend from "inner" selement collections (it is needed obviously only for "inner" selement collection element classes)

## 0.0.6 (released 22.02.2016)
- added alias methods:
```
    insist_not = assure_not
    should_not = assure_not
    should_not_be = assure_not
    should_not_have = assure_not
```
- removed stopit from dependencies
- optimized element actions (now they wait for visibility only if first try failed)
  - now selene is as fast as selenium with research of elements before any action. Manual cashing is also available when "raw selenium" speed is needed (semi-automatic customizable cashing will be added later)
- optimized SElementsCollection#find implementation - now it returns first match, not filter everything and then get first among all matches
- mapped all webelement methods to selement (almost all) - now autocompletion works fully for selement
- optimized logic of "inner lazy elements" of collection, removed a bit of magic from it.

## 0.0.5 (released 20.02.2016)

- big refactoring
  - removed currently unstable things
    - automatic driver management (Firefox)
        - so now management is manual but you can use any driver you want (Firefox, Chrome, etc...)
    - screenshooting
  - removed "too complicated" things
    - automatic Loading of widgets
      - so now no any difference between insist, assure, should
  - added aliases (maybe too much... some may be marked as deprecated in future)
    - insist, assure, should, should_be, should_have
    - find more in elements.py, etc.
  - added more overloaded element methods... removed some magic in implementation, still needed to simplify more...
  - added tests, still not enough though
  - added support of other locators (in addition to css)

## 0.0.4
...
## 0.0.3
...
## 0.0.2
...
## 0.0.1
...
