# How to work with clipboard in Selene? {: #clipboard-copy-and-paste-howto}

{% include-markdown 'warn-from-next-release.md' %}

## Summary

Selene works with clipboard via the [pyperclip](https://pypi.org/project/pyperclip/) package. And there is only one command in Selene that uses it under the hood – [command.paste(text)][selene.core.command.paste]. In other cases you can use `pyperclip` directly to achieve your goals via `paperclip.copy(text)` and `paperclip.paste(text)`.

Let's consider the main scenarios to work with clipboard...

## Main Scenarios

### Copy a text into clipboard

```python
import pyperclip
...

pyperclip.copy('text to copy')
```

### Copy a text of element into clipboard

```python
from selene import browser, query
import pyperclip
...

pyperclip.copy(browser.element('.message').get(query.text))
```

See also [#573](https://github.com/yashaka/selene/issues/573)

### Copy a value of an input element into clipboard

```python
from selene import browser, query
import pyperclip
...

pyperclip.copy(browser.element('input').get(query.value))
```

### Copy currently selected text on the page into clipboard via OS-based shortcut

```python
from selene import browser, command
...

browser.perform(command.copy)
```

See also [#575](https://github.com/yashaka/selene/issues/575)

### Paste into currently focused element a text from the clipboard via OS-based shortcut

```python
from selene import browser, command
...

browser.perform(command.paste)
```

See also [#575](https://github.com/yashaka/selene/issues/575)

### Put a text in the clipboard, then paste it into currently focused element via OS-based shortcut

```python
from selene import browser, command
...

browser.perform(command.paste('some text to put into clipboard first'))
```

See also [#575](https://github.com/yashaka/selene/issues/575)

### Select value of an input element, then copy it into clipboard via OS-based shortcut

```python
from selene import browser, command
...

browser.element('input').select_all().copy()
# OR:
browser.element('input').select_all().perform(command.copy)
```

### Type a text stored in the clipboard into text input at the current cursor position

```python
from selene import browser
import pyperclip
...

browser.element('input').type(pyperclip.paste())
```

### Set a new value to the text input getting this value from the clipboard

```python
from selene import browser
import pyperclip
...

browser.element('input').set_value(pyperclip.paste())
```

### Paste via OS-based shortcut a text stored in the clipboard into text input at the current cursor position

```python
from selene import browser, command
...

browser.element('input').paste()
# OR:
browser.element('input').perform(command.paste)
```

### Paste via OS-based shortcut a text stored in the clipboard into text input substituting the current text via "select all" OS-based shortcut

```python
from selene import browser, command
...

browser.element('input').select_all().paste()
# OR:
browser.element('input').select_all().perform(command.paste)
```

### Copy a text into clipboard, then paste it via OS-based shortcut into text input at the current cursor position

```python
from selene import browser, command
...
text = 'text to append'
browser.element('input').paste(text)
# OR:
browser.element('input').perform(command.paste(text))
```

### Copy a text into clipboard, then paste it via OS-based shortcut into text input substituting the current text via "select all" OS-based shortcut

```python
from selene import browser, command
...
text = 'new text value'
browser.element('input').select_all().paste(text)
# OR:
browser.element('input').select_all().perform(command.paste(text))
```
