# Changelog

## 2.0.0a8 (to be released on 06.01.2020)
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
