# Basic Selene commands cheatsheet

## Find elements

### Basic location
* `browser.element(selector)` – finds element by selector
* `element.element(selector)` – finds inner element inside another element denoted as element (e.g. saved as `element = browser.element(selector)`)
* `element.all(selector)` – finds inner collection of elements
* `browser.all(selector)` – finds collection of elements by selector

### Filtering collections
* `collection.by(condition)` – filters collection by condition (where `collection` – saved collection, e.g. via `collection = browser.all(selector)`; `condition` – anything from `be.*` or `have.*`)
* `collection.element_by(condition)` – finds element of collection by condition
* `collection[index]` or `collection.element(index)` – selects element from collection by index (there are shortcuts – `.first` for `[0]` and `.second` for `[1]`)
* `collection[start:stop:step]` – makes slice of collection starting from `start`, ending before `stop`, with step `step` (there are shortcuts – `.odd` for `[::2]` and `.even` for `[1::2]`; there is an alias `sliced(start, stop, step)` for `[start:stop:step]`)


#### Advanced filtering

Commands like ...

* `collection.by_their(selector, condition)`
* `collection.element_by_its(selector, condition)`
* `collection.all(selector)`
* `collection.all_first(selector)`

... are used less often, and docs about them can be read by diving into their implementation (there are detailed docstrings). Also you can find examples and explanations of these commands in FAQ as an answer to the question “How to find the desired row in the table by condition ...”.

## Check conditions

* `(element | collection | browser).should(condition)` – waits until condition is met, and fails if not
* `(element | collection | browser).wait_until(condition)` – waits until condition is met and returns `false` if not, otherwise `true`
* `(element | collection | browser).matching(condition)` – immediately checks condition and returns `false` if not, otherwise `true`


## Advanced

### Acquiring information from elements

In Selene you cannot just pull out the text or some attribute from the element. This is done on purpose, because Selene aims to promote the implementation of efficient tests. Good tests are those in which the tester knows in advance what will be on the UI at every moment in time, so he does not need to ask the element for its text or the value of a specific attribute, he either knows it, or performs a check through `.should(have.text('something'))` or `.should(have.attribute('data').value('bar'))`. And if you don't know what you have on your UI, then you are writing a crutch (~ workaround) :) And for crutches – Selene adds “extra API”, which is less concise and makes you write crutches more consciously. For these crutches, the following commands may be useful ...

* `element.locate()` – will return a clean Selenium WebDriver WebElement, from which you can then get custom attributes, for example `element.locate().get_attribute('src')`
* `element()` – shortcut to `.locate()`, so in real code it may look like `browser.element('#foo')().get_attribute('src')`
* `element.get(query.*)` – waits for the command-query to be executed on the element and returns the result, for example: `browser.element('#foo').get(query.attribute('src'))`, unlike `browser.element('#foo').locate().get_attribute('src')` – waits for the element to appear at least in the DOM and returns the value of the `'src'` attribute of this element
* `collection.locate()` or `collection()` – will return a list of clean WebElements
* `collection.get(query.*)` – there is also, if you find a request for working specifically with a collection among `*`
* `browser.get(query.*)` – there is also, for example `browser.get(query.title)` should return the title of the page (the text inside the `title` tag inside the HTML)


### Extra commands on elements

* `(element | collection | browser).perform(command.*)` – waits for the command to be executed, for example `browser.element('#approve').perform(command.js.click)` or `browser.all('.addvertisment').perform(command.js.remove)`