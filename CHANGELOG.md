# Changelog

## 0.0.6
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
- optimized "inner lazy elements" of collection logic, removed a bit magic from it.

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
