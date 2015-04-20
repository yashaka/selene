# Selene

Concise API for Selenium in Python + Ajax support + PageObjects + Widgets (Selenide/Capybara + Widgeon alternative)

NOTE: This is still a pre-alpha version with some critical issues, it is NOT READY to be used on a real project.

## Installation

    pip install selene

## Usage

### Basic example

```python
from selene.tools import *
from selene.conditions import text, texts, absent


def test_create_task():
    tasks = ss("#todo-list>li")

    visit("http://todomvc.com/examples/troopjs_require/#/")

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set(task_text).press_enter()
    tasks.insist(texts("1", "2", "3"))
    s("#todo-count").insist(text(3))

    tasks[2].s(".toggle").click()
    s("#filters a[href='#/active']").click()

    tasks[:2].insist(texts("1", "2"))
    tasks[2].insist(absent)
```

### PageObjects and Widgets (aka SElements)

**TBD**

### More examples

See **/tests** files for more examples of usage.

## TODO list

* see todo.md

## Contributing

1. Fork it ( https://github.com/[my-github-username]/py-widgeon/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
