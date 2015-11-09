# 0.1.0
## Changes
- added support of any locator to find an element
- added/updated conditions: absent, present, has_text
- added methods to SElement: is_visible, is_present, has_text
- added method to SElementsCollection: is_empty
- added method to execute any JS script and remove 'readonly' attribute from element
- refactor waits.py module

## Migration from 0.0.4
- both SElement and  SElementsCollection initialization was changed. Make sure you pass correct parameters 
in ```__init__()``` method. 
- replace all imports from ```from selene.tools import ...``` to ```from selene import ...```
- if element isn't found, ```selene.waits.ExpiredWaitingException``` will be raised instead of 
```stopit.TimeoutException```

# 0.0.4
Initial published version.