# Selene in action

After the [quick introduction to the basics](./selene-quick-start-tutorial.md) of working with Selene, let's get more acquainted with the most commonly used elements of their syntax on the example of implementing a test scenario for the application – task manager – [TodoMVC](https://todomvc-emberjs-app.autotest.how/).

```python
# selene-intro/tests/test_todomvc.py 

# ... imports




def test_adds_and_completes_todos():
    # open TodoMVC page

    # add todos: 'a', 'b', 'c'
    # todos should be 'a', 'b', 'c'

    # toggle 'b'
    # completed todos should be 'b'
    # active todos should be 'a', 'c'
    pass
```

Let's play with this application, let's try to repeat this scenario manually...

![](../assets/images/selene-in-action-tutorial.md/todomvc-app.png)


And immediately let's dig into the structure of html for such a set of tasks...

![](../assets/images/selene-in-action-tutorial.md/todomvc-app-inspect.png)

... paying attention to the elements with which we interact, and ignoring those elements that we are not interested in yet:

```html
<section id="todoapp">
  <header id="header">
    <!-- ... -->
    <input type="text" id="new-todo" placeholder="What needs to be done?" autofocus="">
  </header>
  <section id="main" class="ember-view">
    <!-- ... -->
    <ul id="todo-list" class="todo-list">
      <li id="ember267" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>a</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
      <li id="ember317" class="completed ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>b</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
      <li id="ember319" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>c</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
    </ul>
  </section>
  <footer id="footer">
    <!-- ... -->
    <ul id="filters">
      <li><a href="#/" id="ember275" class="selected ember-view">All</a></li>
      <li><a href="#/active" id="ember282" class="ember-view">Active</a></li>
      <li><a href="#/completed" id="ember298" class="ember-view">Completed</a></li>
    </ul>
    <!-- ... -->
  </footer>
</section>
```

Here they are, these elements, needed for the corresponding actions of our scenario:

- add "a", "b", "c"

```html
    <input type="text" id="new-todo" placeholder="What needs to be done?" autofocus="">
```

- todos should be "a", "b", "c"

```html
    <ul id="todo-list" class="todo-list">
      <li id="ember267" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>a</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
      <li id="ember317" class="completed ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>b</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
      <li id="ember319" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>c</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
    </ul>
```

- toggle "b"

```html
      <li id="ember317" class="completed ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">    <!-- <<< -->
          <label>b</label>
```

- completed todos should be b

```html
      <li id="ember317" class="completed ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>b</label>
          <!-- ... -->
        </div>
        <!-- ... -->
```

- active todos should be a, c

```html
    <ul id="todo-list" class="todo-list">
      <li id="ember267" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>a</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
      <li id="ember319" class="ember-view">
        <div class="view">
          <input type="checkbox" class="toggle">
          <label>c</label>
          <!-- ... -->
        </div>
        <!-- ... -->
      </li>
    </ul>
```

Now, knowing the “characteristics” of our elements – their attributes, we [will be able to find them](https://autotest.how/qaest/css-selectors-guide-md) in the code and perform the necessary actions, only if we knew how to find them and how to interact with them.

Well, let's go, let's implement our scenario:

```python

def test_adds_and_completes_todos():

    # open TodoMVC page

    # add todos: 'a', 'b', 'c'
    # todos should be 'a', 'b', 'c'

    # toggle 'b'
    # completed todos should be 'b'
    # active todos should be 'a', 'c'
    pass
```

For the first step, the command is obvious, we just need to pass the required URL as a parameter to `open`:

```python
# open TodoMVC page
browser.open('https://todomvc-emberjs-app.autotest.how/')

# add todos: 'a', 'b', 'c'
# todos should be 'a', 'b', 'c'

# toggle 'b'
# completed todos should be 'b'
# active todos should be 'a', 'c'
```

For the next step, we need to remember the sequence of actions for adding one task:

```python
#...

# add todo 'a':
#    1. find "new todo" text field 
#                               2. type 'a'
#                                         3. press Enter
```

Now, translating this into the “language of selene” will not be difficult, using IDE hints to find the commands we need to perform actions on the element:

```python
#...

# add todo 'a':
#1. find              "new todo" text field 
#                               2. type 'a'
#                                         3. press Enter
browser.element(by.id('new-todo')).type('a').press_enter()

```

We use the `browser.element` command to access the element on the page ...

```html
<input type="text" id="new-todo" placeholder="What needs to be done?"
       autofocus="">
```

... by locator, finding the element by a unique identifier:

```python

by.id('new-todo')
```

You can use a CSS selector, passing it directly to the `browser.element` command, and get a slightly more concise code:

```python

browser.element('#new-todo').type('a').press_enter()
```

Even more concisely, you can write the same line using the `s` command:

```python
s('#new-todo').type('a').press_enter()
```

But let's limit ourselves to the previous version for now, let it be less concise, but more readable for most beginners, who probably do not know yet, ;) that in the world of frontend – the dollar is a “standard” command to search for elements by selector, which is usually available in the browser console.

Now you can add other todos using a very useful approach – “Copy & Paste Driven Development” ;)

```python
#...

# add todos 'a', 'b', 'c'
browser.element('#new-todo').type('a').press_enter()
browser.element('#new-todo').type('b').press_enter()
browser.element('#new-todo').type('c').press_enter()

# todos should be 'a', 'b', 'c'
# ...
```

Now let's find all todos in the list using the `browser.all` command and check that they have the corresponding texts:


There is also a corresponding “shortcut” for this command:
 
```python
ss('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))
```

As you can see, the “selene language” is not very different from the “English” ;)

Checks (aka “assertions” in test automation) on elements or collections of elements, as in the last case, are performed using the `should` command, which is passed a condition to check.


```python
# add todos 'a', 'b', 'c'
browser.element('#new-todo').type('a').press_enter()
browser.element('#new-todo').type('b').press_enter()
browser.element('#new-todo').type('c').press_enter()

# todos should be 'a', 'b', 'c'
browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))
```

Condition sets are available through the `have.*` syntax, which allows you to compose code in the form of readable English phrases.

But “should + have” is probably not enough to cover all the options for telling the story about checking elements in English language ;). So another set of conditions lives in `be.*`. Let's come up with an example for using `be.*` in our test too ;)

Pay attention that if you look at the “source” of the TodoMVC web page in the browser:

![](../assets/images/selene-in-action-tutorial.md/view-page-source-of-todomvc-with-no-todos-in-chrome.png)

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>Todomvc</title>
<meta name="description" content="">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="todomvc/config/environment" content="%7B%22modulePrefix%22%3A%22to
domvc%22%2C%22environment%22%3A%22production%22%2C%22baseURL%22%3Anull%2C%22lo
cationType%22%3A%22hash%22%2C%22EmberENV%22%3A%7B%22FEATURES%22%3A%7B%7D%2C%22
EXTEND_PROTOTYPES%22%3A%7B%22Date%22%3Afalse%7D%7D%2C%22APP%22%3A%7B%22name%22
%3A%22todomvc%22%2C%22version%22%3A%220.0.0+47754603%22%7D%2C%22exportApplicat
ionGlobal%22%3Afalse%7D" />

<link rel="stylesheet" href="assets/vendor7b5c98520910afa58d74e05ec86cd
873.css" integrity="sha256bsagGHduhay9QPLUFpddcZFq7Kmr2ScM3VKnWhdX8oM=sha512eN
sGN2aLecWPvoqNVH8oXK8o/IJ7rO5ti0zgS8lF8LiwmKUHdEIuFduwcDL1VLAt2r+3YjgDzoSNYK6c
57pJzw==" >
<link rel="stylesheet" href="assets/todomvcd41d8cd98f00b204e9800998ecf842
7e.css" integrity="sha25647DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU= sha51
2z4PhNX7vuL3xVChQ1m2AB9Yg5AULVxXcg/SpIdNs6c5H0NE8XYXysP+DGNKHfuwvY7kxvUdBeoGlODJ6+SfaPg==" >

</head>

<body>

<script src="assets/vendor-22a6a947beb9d4b28a782879e18b0f65.js" integrity="sha
256-M1pD1q8B9PyrHkKX/mlfsOLLHMrh/x7vvCGLRC63OyI= sha512-I4vC6+4Z29iHB4nJBCzcIj
rgMtDerq7sxYLE2lM/AhjkNLp6gf2+Zpne8OtGdTLRkyvTqzPm1V7gq9w4HQxOXg==" >
</script>
<script src="assets/todomvc-d191d5c1c9280b108d69413f052d3bb4.js" integrity="sh
a256-1wUxToLQP6yjsvm0/8e3xQnv7SbSYcj3P/OPEdThZOk= sha512-X5K7gsPRYsUSRvJcnj80S
LlclDd4X/g1Qgle1L1P4Zb63eUM0mYEfQECBcjcks7iZFItSGr8EVPOVELXO35HUA==" >
</script>

</body>
</html>
```

– it turns out that there are no familiar to us elements there, like the `#new-todo` one! This means, at least, that these elements are added dynamically after loading the html page using JavaScript. That is, they are really “appearing on the page after loading”, not immediately. And, of course, it takes some time. Maybe we just got lucky – nothing was slowing down, and JavaScript dynamically added our `#new-todo` element fast enough so that we could continue our scenario. Well, maybe... – it is not always lucky for us, and it is worth anticipating this moment and waiting for the visibility of the element before performing the necessary actions:

```python
browser.element('#new-todo').should(be.visible).type('a').press_enter()
```

The `should` command plays exactly the role of “explicit waiting for the moment when the element will satisfy the condition”, and not only performs a check by the condition... You can also say that in checks using `should` there is an “implicit waiting” built in.

And now the good news - in fact, you don't need to write `.should(be.visible)` before each action. The library engine itself will wait until the element is available to perform an action on it, so it is enough:

```python
browser.element('#new-todo').type('a').press_enter()
```

In such cases we say that more powerful “implicit waits” are built into the actions themselves, in addition to the waits built into the checks on elements (aka “assertions”). This is one of the main differences between Selene and “pure” Selenium Webdriver. Selenium implicit waits are disabled by default and if enabled – wait only until the element appears in the DOM (html page), but at the same time the element may still be invisible and therefore not available for interaction, which will lead to a test failure. Or – till the end of loading – the element may be covered by another element, and therefore still will not be available for performing certain actions on it, for example `click`. In Selene, however, the expectations wait until the “action or check passes”. By default, they are enabled, with a default timeout of `4` seconds. The timeout can be specified explicitly either when configuring the browser:

```python
browser.config.timeout = 6

# ...

browser.element('#new-todo').type('a').press_enter()
```
or when customizing a specific element or collection of elements:

```python
# ...


browser.element('#new-todo').with_(timeout=6).type('a').press_enter()

# ...

browser.all('#todo-list>li').with_(timeout=2).should(have.exact_texts('a', 'b', 'c'))

# the following will also work:
# browser.with_(timeout=6).all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))
```
This `browser.config` is a whole warehouse of various options for configuring the behavior of the library and its commands, be sure to explore all the possible options ;)

For example, by changing the corresponding option, you can change the type of browser used, and instead of running tests in Chrome, run them in Firefox:

```python


browser.config.browser_name = 'firefox'
```
Let's go back to our scenario...

```python
# open TodoMVC page
browser.open('https://todomvc-emberjs-app.autotest.how/')

# add todos: 'a', 'b', 'c'
browser.element('#new-todo').type('a').press_enter()
browser.element('#new-todo').type('b').press_enter()
browser.element('#new-todo').type('c').press_enter()

# todos should be 'a', 'b', 'c'
browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

# toggle 'b'
# completed todos should be 'b'
# active todos should be 'a', 'c'
```
– and finish its implementation ;)

The next step is to mark the task as “completed”. To do this, you need:

```python
# ...

# toggle b:

# 1:among all todos
#                          2:find the one with     text 'b'
#3:  find its 'toggle' checkbox
#                     4:click it
```
In Selene, this is very easy:

```python
# ...

# toggle b:

# 1:among all todos
#                          2:find the one with     text 'b'
browser.all('#todo-list>li').element_by(have.exact_text('b'))\
    .element('.toggle').click()
#                     4:click it
#3:  find its 'toggle' checkbox
```
As you can see, to find the required element among other elements of the collection, we use the same type of condition (“condition”) as for “waiting-checks”. Without such possibilities, in ordinary Selenium Webdriver, we would have to use bulkier and less readable XPath-selector.

The final steps are responsible for checking the result of the previous action:

```python
# ...

# todos should be 'a', 'b', 'c'
browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

# toggle 'b'
browser.all('#todo-list>li').element_by(have.exact_text('b'))\
    .element('.toggle').click()

# completed todos should be 'b':
    # among all todos – filter only completed ones – check their texts
# active todos should be 'a', 'c':
    # among all todos – filter only not completed ones – check their texts
```
The translation into the “selene language” is still just as simple:

```python
# ...

# completed todos should be 'b':

#1:among all todos
                          #2:filter only        completed ones
browser.all('#todo-list>li').by(have.css_class('completed'))\
    .should(have.exact_texts('b'))
  #3:check  their      texts

# active todos should be 'a', 'c':

#1:among all todos
                          #2:filter  not           completed ones
browser.all('#todo-list>li').by(have.no.css_class('completed'))\
    .should(have.exact_texts('a', 'c'))
  #3:check  their      texts
```

As you can see, in general, the code really becomes so readable that our current comments...

```python
# open TodoMVC page
browser.open('https://todomvc-emberjs-app.autotest.how/')

# add todos: 'a', 'b', 'c'
browser.element('#new-todo').type('a').press_enter()
browser.element('#new-todo').type('b').press_enter()
browser.element('#new-todo').type('c').press_enter()

# todos should be 'a', 'b', 'c'
browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

# toggle 'b'
browser.all('#todo-list>li').element_by(have.exact_text('b'))\
    .element('.toggle').click()

# completed todos should be 'b'
browser.all('#todo-list>li').by(have.css_class('completed'))\
    .should(have.exact_texts('b'))

# active todos should be 'a', 'c'
browser.all('#todo-list>li').by(have.no.css_class('completed'))\
    .should(have.exact_texts('a', 'c'))
```
are no longer needed:

```python
browser.open('https://todomvc-emberjs-app.autotest.how/')

browser.element('#new-todo').type('a').press_enter()
browser.element('#new-todo').type('b').press_enter()
browser.element('#new-todo').type('c').press_enter()
browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

browser.all('#todo-list>li').element_by(have.exact_text('b'))\
    .element('.toggle').click()
browser.all('#todo-list>li').by(have.css_class('completed'))\
    .should(have.exact_texts('b'))
browser.all('#todo-list>li').by(have.no.css_class('completed'))\
    .should(have.exact_texts('a', 'c'))
```

These basic commands, support for functions “Autocomplete” and “Quick Fix” from IDE, the courage to dig into the code, and finally, the official documentation - should be quite enough to start writing the first tests with Selene.

Good luck ;)