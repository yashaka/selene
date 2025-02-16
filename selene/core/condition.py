# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
## Overview

Conditions, or "expected conditions" (as they
[are called in Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/support_features/expected_conditions/)),
or matchers (as they are called in [PyHamcrest](https://github.com/hamcrest/PyHamcrest))
– are callable objects or functions that once called on some entity –
test if the entity matches the corresponding criteria of a condition,
and then, if matched, simply pass, or raise an error otherwise.
They are used in testing to flexibly implement test assertions
and explicit waits that are also relevant in context of
"asserting dynamic behavior of some entities", like elements
on the dynamically loaded page.

!!! note

    In Selenium WebDriver the valid condition is also a simple predicate function,
    i.e. the function returning True or False, and it's not mandatory
    for the condition in Selenium to raise an error to signal "not matched" state
    – returning False is enough. In Selene, it's not the case –
    the condition should raise an Error to signal "not matched" state.
    In Selene such design decision is a base for powerful logging abilities
    of conditions in context of their failures.
    Since a condition owns a knowledge of its criteria to be matched,
    it seems to be the best place
    (in context of following the "high cohesion" principle)
    to define how this criteria will be logged if not matched –
    what naturally happens on raising a "not matched" error.

    From other point of view – the True|False-predicate-based conditions
    are easier to define. To keep similar level of easiness, Selene provides
    additional helpers (like
    [`ConditionMismatch._to_raise_if_not(predicate)`][selene.core.exceptions.ConditionMismatch._to_raise_if_not])
    and the [`Match`][selene.core.condition.Match] to build conditions based on
    predicates. While the base class of Match – the
    [`Condition`][selene.core.condition.Condition] class currently has stable API only
    for Pass|Fail-function-based matchers). More on their usage below.

## Predefined conditions

### match.\* VS be.\* & have.\*

Usually you don't need to build conditions yourself, they are predefined
for easier reuse. In Selene, they are predefined in
[`match.*`](../match) and can be accessed additionally via
[`be.*`](../be) and [`have.*`](../have)
syntax.

`match` is handy because it's a "one term to learn and one import to use":

```python
from selene import browser, match

browser.should(match.title('Selene'))
browser.element('#save').should(match.enabled)
browser.element('#loading').should(match.visible.not_)
browser.element('#field').should(match.exact_text('hello'))
browser.element('#field').should(match.css_class('required').not_)
```

`be` and `have` force to use "more imports" but are more "high level"
and might help to write more readable code:

```python
from selene import browser, be, have

browser.should(have.title('Selene'))
browser.element('#save').should(be.enabled)
browser.element('#loading').should(be.not_.visible)
browser.element('#field').should(have.exact_text('hello'))
browser.element('#field').should(have.no.css_class('required'))
```

### Extending predefined conditions (Demo)

Because `match` is "just one term", it might be easier also
to "extend Selene's predefined conditions" with your custom ones,
because you have to deal only with "one module re-definition", like in:

```python
# Full path can be: my_tests_project/extensions/selene/match.py
from selene.core.match import *
from selene.core import match as __selene_match
from selene.support.conditions import not_ as __selene_not_

not_ = __selene_not_


# An example of a new condition definition
def no_visible_alert(browser):
    try:
        text = browser.driver.switch_to.alert.text
        raise AssertionError('visible alert found with text: ' + text)
    except NoAlertPresentException:
        pass


# Maybe you don't like the match.exact_text + match.text_containing conditions naming
# and decide to override it:

def text(expected):
    return __selene_match.exact_text(expected)


def partial_text(expected):
    return __selene_match.text_containing(expected)
```

So we can use it like:

```python
from selene import browser
from my_tests_project.extensions.selene import match

browser.should(match.no_visible_alert)
browser.should(match.title('Selene'))
browser.element('#save').should(match.enabled)
browser.element('#loading').should(match.not_.visible)
browser.element('#field').should(match.text('hello'))
browser.element('#field').should(match.partial_text('hel'))
browser.element('#field').should(match.not_.css_class('required'))
```

From other side, you do it once, so maybe it's not like that hard
to redefine "more readable" `be` and `have`
to extend predefined Selene conditions and forget about it:).
The choice is yours...
Maybe even all your extended conditions will be "have" ones:

```python
from selene import browser, be
from my_tests_project.extensions.selene import have

browser.should(have.no_visible_alert)
browser.should(have.title('Selene'))
browser.element('#save').should(be.enabled)
browser.element('#loading').should(be.not_.visible)
browser.element('#field').should(have.text('hello'))
browser.element('#field').should(have.partial_text('hel'))
browser.element('#field').should(have.no.css_class('required'))
```

!!! info

    If you need a more detailed explanation of how we "extended" Selene's predefined
    conditions in the example above, look at the
    [How to implement custom advanced commands?][selene.core.command--how-to-implement-custom-advanced-commands]
    article, that explains same pattern for the case of extending Selene
    predefined commands.

## Functional conditions definition

Ok, now, let's go deeper into how to define custom conditions starting from
function-based conditions.

!!! tip

    Function-based conditions are the simplest ones in Selene,
    and they are limited in reusability during definition of new conditions
    based on existing ones.
    [Object-oriented conditions][selene.core.condition--object-oriented-re-composable-conditions-demo]
    are more powerful. But understanding how to define functional conditions
    is crucial to understand how to define object-oriented ones,
    as the latter are built on top of the former.
    Thus, we recommend not to skip this section if you are new to the topic.

!!! tip

    If you are an experienced SDET engineer, and are familiar with the concept
    of expected conditions and how to define them e.g. in Selenium WebDriver,
    and want a fast way to get familiar with how to define most powerful
    custom conditions in Selene, jump directly to the examples of
    [`Match`][selene.core.condition.Match] class usage.
    In case of any doubts on the topic, read on this article without skipping
    any section.

### Pass|Fail-function-based definition

The simplest way to implement a condition in Selene is to define a function
that raises AssertionError if the argument passed to the function
does not match some criteria:

```python
def is_positive(x):
    if not x > 0:
        raise AssertionError(f'Expected positive number, but got {x}')
```

### True|False-predicate-based definition

Or in one-liner if we use
[`ConditionMismatch`][selene.core.exceptions.ConditionMismatch] factory method
to build a condition from predicate:

```python
is_positive = ConditionMismatch._to_raise_if_not(lambda x: x > 0)
```

### Condition application

Then we test a condition simply by calling it:

```python
is_positive(1)      # ✅ passes
try:
    is_positive(0)  # ❌ fails
except AssertionError as error:
    assert 'Expected positive number, but got 0' in str(error)
```

But really useful conditions become when used in waits:

```python
def has_positive_number(entity):
    number = entity.number
    if not number > 0:
        raise AssertionError(f'Expected positive number, but got {number}')

class Storage:
    number = 0

# imagine that here we created an async operation
# that after some timeout will update number in storage - to > 0

from selene.core.wait import Wait

Wait(Storage, at_most=1.0).for_(has_positive_number)
```

!!! note

    In Selene the Wait object is usually built under the hood,
    and we would see something like:

    ```python
    Storage.should(has_positive_number)
    ```

    where:
    ```python
    class Storage:
        number = 0

        @classmethod
        def should(cls, condition):
            Wait(cls, at_most=1.0).for_(condition)
    ```

    Now recall the actual Selene assertion on browser object:

    ```python
    browser.element('#save').should(be.enabled)
    ```

    😉

### Rendering in error messages

If wait did not succeed, it will raise an error with a message like:

```text
Timed out after 1.0s, while waiting for:
<class 'Storage'>.has_positive_number
Reason: AssertionError: Expected positive number, but got 0
```

– as you see the message is quite informative and helps to understand
what happened. Pay attention that the name `has_positive_number`
of our condition-function was used in error message to explain
what we were waiting for.

#### Improving error messages of lambda-based conditions

But what if we used a lambda predicate to define the condition:

```python
from selene.core.exceptions import ConditionMismatch

has_positive_number = ConditionMismatch._to_raise_if_not(
    lambda entity: entity.number > 0
)
```

Then error would be less informative, because lambda is anonymous –
there is no way to build a name for it:

```text
Timed out after 1.0s, while waiting for:
<class 'Storage'>.<function <lambda> at 0x106b5d8b0>
Reason: ConditionMismatch: actual: 0
```

To fix this, we can provide a name for the lambda
by wrapping it into Query:

```python
from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import Query

has_positive_number = ConditionMismatch._to_raise_if_not(
    Query('has positive number', lambda entity: entity.number > 0)
)
```

Now error would look quite informative again:

```text
Timed out after 1.0s, while waiting for:
<class 'Storage'>.has positive number
Reason:  ConditionMismatch: actual: 0
```

### Choosing the style to define functional conditions

Feel free to choose the way that fits your needs best among:

- Pass|Fail-function-condition
- True|False-lambda-predicate-condition
    built with wrapped lambda into `Query` and `ConditionMismatch._to_raise_if_not`.

#### Basic refactoring of conditions

Utilizing `ConditionMismatch` gives also an option
to "break down the predicate logic" into two steps:

- querying the entity for needed value
- applying predicate to the value

This is performed by adding additional query function,
to get something useful from the entity before applying the predicate:

```python
has_positive_number = ConditionMismatch._to_raise_if_not(
    lambda number: number > 0,
    lambda entity: entity.number,
)
```

And now we know how to benefit from more descriptive error messages
by providing names for our lambdas as follows:

```python
has_positive_number = ConditionMismatch._to_raise_if_not(
    Query('is positive', lambda number: number > 0),
    Query('number', lambda entity: entity.number),
)
```

In case we already have somewhere defined queries:

```python
is_positive = Query('is positive', lambda number: number > 0)
number = Query('number', lambda entity: entity.number)
```

The condition definition becomes even more concise and readable:

```python
has_positive_number = ConditionMismatch._to_raise_if_not(is_positive, number)
```

#### Parametrized conditions

Another example of common usage is the definition of a parametrized condition:

```python
has_number_more_than = lambda limit: ConditionMismatch._to_raise_if_not(
    is_more_than(limit),
    number,
)
```

– where:

```python
is_more_than = lambda limit: Query('is more than', lambda number: number > limit)
number = Query('number', lambda entity: entity.number)
```

Or with regular functions:

```python
def has_number_more_than(limit):
    return ConditionMismatch._to_raise_if_not(is_more_than(limit), number)
```

– where:

```python
number = Query('number', lambda entity: entity.number)
def is_more_than(limit):
    return Query('is more than', lambda number: number > limit)
```

## Object-Oriented re-composable conditions Demo

This is enough for simpler cases, but what if we want to be able to compose
new conditions based on existing ones, like in:

```
# wait for not negative even number
Wait(Storage, at_most=1.0).for_(has_positive_number.and_(has_even_number).not_)
```

Here comes in rescue the [`Condition`][selene.core.condition.Condition] class
and its [`Match`][selene.core.condition.Match] subclass, allowing to build such
"re-composable" conditions.

## ⬇️ Classes to build and recompose conditions
"""
from __future__ import annotations

import functools
import sys
import typing
import warnings

from selenium.common import WebDriverException
from typing_extensions import (
    List,
    TypeVar,
    Generic,
    Iterable,
    Tuple,
    Optional,
    Self,
    override,
    cast,
    overload,
    Union,
    Type,
)

from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import Lambda, Predicate, E, R, Query

# TODO: shouldn't we just import if from typing_extensions?
if sys.version_info >= (3, 10):
    from collections.abc import Callable
else:
    from typing import Callable


# TODO: Consider renaming to Match, while keeping Condition name as functional interface
class Condition(Generic[E]):
    """Class to build, invert and compose "callable matcher" objects,
    that conforms to `Callable[[E], None | <RAISED ERROR>]` protocol,
    and represent the "conditions that can pass or fail when tested or
    so called "matched" against an entity". So, once called on some entity of type E
    such condition object should test if the entity matches the condition object,
    and then simply pass if matched or raise AssertionError otherwise.

    !!! note

        You can find using the "match" term in different forms, depending on context.
        It may confuse a bit. Assume the following...

        If you see in the code "match", i.e. as a "verb in the imperative mood"
        or as a "noun", then, usually, the "assertion" is meant, i.e.
        "test a condition against an entity, then pass if matched or fail otherwise".
        For example: `element.should(match.visible)` or
        `number.should(Match('is positive'), by=lambda it: it > 0)` or
        `number.wait.for_(Condition('is positive', match=ConditionMismatch._to_raise_if_not(lambda it: it > 0)))`.

        If you see "matching", i.e. as a "verb in present participle", then
        the "predicate application" will be forced, i.e.
        "test a condition against an entity, then return True if matched or False otherwise".
        For example: `element.matching(be.visible)` or even `element.matching(match.visible)`
        (the "matching" meaning kind of "overrides the match one").

        Yes, `matching(match.*)` – look a bit weird, but firstly,
        there more readable alternatives like `matching(be.*)` or simply `matching(*)`, and,
        secondly, if your tests are implemented according to best practices,
        you will rarely need applying condition as predicate ;).

        There is also an alternative, a bit more readable way to check the
        "matching" result: `match.visible._matching(element)` – but take into account
        that the `_` prefix in `condition._matching` marks the method as a part
        of Selene's experimental API, that may change with the time.

    ### When to use Condition-object-based definition

    For most cases you don't need this class directly,
    you can simply reuse the conditions predefined in [`match.*`](../match).

    You will start to need this class when you want to build your own custom conditions
    to use in a specific to your case assertions.
    And even then, it might be enough to use a simpler version of this class –
    its [Match][selene.core.condition.Match] subclass that has handier bunch of params
    to set on constructing new condition, that is especially handy
    when you build conditions inline without the need to store and reuse them later,
    like in:

    ```python
    from selene import browser
    from selene.core.condition import Match
    input = browser.element('#field')
    input.should(Match(
        'normalized value',
        by=lambda it: not re.find_all(r'(\s)\1+', it.locate().get_attribute(value)),
    ))
    ```

    For other examples of using `Match`, up to something as concise
    as `input.should(Match(actual=query.value, by=is_normalized))`,
    see [its section][selene.core.condition.Match].

    And for simplest scenarios you may keep it most KISS
    with "Pass|Fail-function-based conditions" or
    "True|False-predicate-based conditions" as described in
    [Functional conditions definition][selene.core.condition--functional-conditions-definition].

    But when you start bothering about reusing existing conditions
    to build new ones on top of them by applying logical `and`, `or`,
    or `not` operators you start to face some limitations of "functional-only"
    conditions...

    Compare:

    ```python
    has_positive_number = ConditionMismatch._to_raise_if_not_actual(
        Query('number', lambda entity: entity.number),
        Query('is positive', lambda number: number > 0),
    )

    has_negative_number_or_zero = ConditionMismatch._to_raise_if_not_actual(
        Query('number', lambda entity: entity.number),
        Query('is negative or zero', lambda number: number <= 0),
    )
    ```

    to:

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )

    has_negative_number_or_zero = has_positive_number.not_
    ```

    !!! note

        If you see
        [ConditionMismatch._to_raise_if_not_actual][selene.core.exceptions.ConditionMismatch._to_raise_if_not_actual]
        for the first time,
        it's similar to
        [ConditionMismatch._to_raise_if_not][selene.core.exceptions.ConditionMismatch._to_raise_if_not],
        but with inverted order of params:
        `ConditionMismatch._to_raise_if_not_actual(number, is_positive)`
        ==
        `ConditionMismatch._to_raise_if_not(is_positive, number)`

    Notice the following ⬇️

    ### Specifics of the Condition-object-based definition

    - It is simply a wrapping functional condition (Pass|Fail-function-based)
        into a Condition object with custom name.
        Thus, we can use all variations of defining functional conditions
        to define object-oriented ones.
    - Because we provided a custom name
        (`'has positive number'` in the case above), it's not mandatory
        to wrap lambdas into Query objects to achieve readable error messages,
        unlike we had to do for functional conditions.

    ### Customizing name of inverted conditions

    The name of the `has_negative_number_or_zero` will be automatically
    constructed as `'has not (positive number)'`. In case you want custom,
    you can simply re-wrap it into a new condition:

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        ),
    )

    has_negative_number_or_zero = Condition(  # ⬅️
        'has negative number or zero',        # 💡
        has_positive_number.not_
    )
    ```

    Same re-wrap can be done with a Match subclass of Condition,
    but with an explicit keyword argument only:

    ```python
    ...

    has_negative_number_or_zero = Match(  # ⬅️
        'has negative number or zero',
        by=has_positive_number.not_
    )  #  ↖️
    ```

    !!! tip

        The "customizing name" pattern above can give a bit more benefits,
        when applied to conditions built via `Match` class by providing
        `actual` and `by` params.

        ```python
        has_positive_number = Match(              # ⬅️
            'has positive number',
            actual=lambda entity: entity.number,  # 💡
            by=lambda number: number > 0,         # 💡
        )

        has_negative_number_or_zero = Condition(
            'has negative number or zero',
            has_positive_number.not_
        )
        '''
        # OR
        has_negative_number_or_zero = Match(
            'has negative number or zero',
            by=has_positive_number.not_
        )
        '''
        ```

        In this case the error message will be a bit more informative,
        logging also the actual value.

    !!! tip

        There is an alternative shortcut to invert a base condition with custom name
        – the `Condition.as_not(base_condition, new_name)` method:

        ```python
        ...

        # compare:
        has_negative_number_or_zero = Condition(
            'has negative number or zero',
            has_positive_number.not_
        )

        # to:
        has_negative_number_or_zero = Condition.as_not(  # ⬅️
            has_positive_number,
            'has negative number or zero',  # 💡
        )
        ```

        It works completely the same under the hood as inverting + wrapping via
        `Condition(new_name, base_condition.not_)`
        or `Match(new_name, by=base_condition.not_)` – it's just a matter of taste.

    ### Customizing name of other composable conditions

    Same "wrap" technique can be used to name conditions composed by logical
    `and` or `or` like in:

    ```python
    hidden_in_dom = Condition('hidden in DOM', present_in_dom.and_(visible.not_))
    blank = Condition('blank', tag('input').and_(value('')).or_(exact_text('')))
    '''
    # OR with a Match subclass
    hidden_in_dom = Match('hidden in DOM', present_in_dom.and_(visible.not_))
    blank = Match('blank', tag('input').and_(value('')).or_(exact_text('')))
    '''
    ```

    ### Re-composing methods summary

    Thus:

    - to invert condition you use `condition.not_` property
    - to compose conditions by logical `and` you use `condition.and_(another_condition)`
    - to compose conditions by logical `or` you use `condition.or_(another_condition)`
    - to override condition name after "composition" you wrap it into a new condition
        via `Condition(new_name, composed_condition)`

    ### Alternative signatures for Condition class initializer

    Condition class initializer has more than two params, not just name and
    functional condition as we have seen above

    - `name` – a required custom name for the condition or a callable on optional
        entity, that will be used to describe the condition in the error message
        depending on the entity, that can be useful in case of multi-entity conditions,
        for example, a `size` condition can work with both "singular" and "plural"
        entities, then we could provide the name as
        `lambda entity: 'have size' if entity is not None and hasattr(entity, '__len__') else 'has size'`
    - `test` – a Pass|Fail-function based condition

    ⬆️ Both these parameters are "positional only". This is an "internal trick of us"
    to postpone the time to decide on the final naming of them. We can hardly choose
    between `name` and `description` for the first one, and between `test` and `match`
    for the second one:), but while they are "positional only" you have nothing
    to worry about on your side;).

    Other params are optional:

    - `_actual` – a callable on entity to get the actual value from it to match.
        Can't be passed if `test` arg was provided. If `test` arg was not provided,
        yet can be skipped, then it will be similar to passing `lambda it: it` as actual
    - `_by` - a callable predicate to check for matching actual value if `_actual`
        was provided or for matching entity itself otherwise. Can't be passed if `test`
        was provided. You have to choose how to define a condition – via `test`
        or via `by` with optional `actual`.
    - `_describe_actual_result` – a callable on the actual value used during match,
        that will be used if match failed to describe the actual value in the error
        message. Currently, will be used only if `_actual` was provided explicitly,
        but this might change in the future...
    - `_inverted` – a boolean flag to mark the condition as inverted. False by default.
    - `_falsy_exceptions` – a tuple of exceptions that should be considered as "falsy"
        if condition was inverted. By default, it's `(AssertionError, )` only.

    All are marked as "experimental/internal" for the following reasons:

    - `_actual` and `_by` might be moved completely from Condition to its Match subclass
        in order to simplify the implementation of the base Condition class,
        taking into account that providing such arguments nevertheless leads to more
        readable code exactly in case of Match, not Condition.
    - `_describe_actual_result` can be renamed (e.g. to `describe_actual` or `describe`)
        and also moved to Match for same reason as `_actual`
    - `_inverted` is planned to be "protected" all the time, in order to force end user
        to use `.not_` property to invert conditions even if they are "inline" ones
    - `_falsy_exceptions` can be renamed and also are marked as "protected"
        to eliminate usage in the "inline" context

    This bunch of params lead to different ways to define conditions.
    Since the Condition class has more params marked as "internal/experimental"
    than the Match class, we will show more of such variations in examples of
    the [Match][selene.core.condition.Match] class usage. And now we provide
    just a few to see the actual difference between defining condition via
    Pass|Fail-function and via True|False-predicate.

    Recall the initial example:

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )
    ```

    or with using `_to_raise_if_not` over `_to_raise_if_not_actual` – they differ
    by order of params:

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not(
            lambda number: number > 0,
            lambda entity: entity.number,
        )
    )
    ```

    But utilizing the named arguments python feature, we can
    define our own order (unless params are defined as positional only,
    and they are not in this case):

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not(
            actual=lambda entity: entity.number,
            by=lambda number: number > 0,
        )
    )
    ```

    #### The core parameter: **test** (2nd positional parameter)

    Regardless of what happens with params to ConditionMismatch class methods,
    the 2nd positional-only param to the Condition initializer is allways the same –
    Pass|Fail-function-based condition.

    #### Parameters: actual and by VS test

    In order to remove a bit of boilerplate on object-oriented condition definition,
    there two other alternative parameters to the Condition class initializer:
    `_actual` and `_by` – similar to the parameters of the
    [`Condition._to_raise_if_not`][selene.core.exceptions.ConditionMismatch._to_raise_if_not]
    helper that we used to define functional True|False-predicate-based conditions.

    Compare:

    ```python
    has_positive_number = Condition(
        'has positive number',
        ConditionMismatch._to_raise_if_not(
            actual=lambda entity: entity.number,
            by=lambda number: number > 0,
        )
    )
    ```

    to:

    ```python
    has_positive_number = Condition(
        'has positive number',
        _actual=lambda entity: entity.number,
        _by=lambda number: number > 0,
    )
    ```

    or by utilizing the [Match][selene.core.condition.Match]
    subclass of Condition, that has `actual` and `by` params as stable
    (not experimental), and so – safer to use:

    ```python
    has_positive_number = Match(
        'has positive number',
        actual=lambda entity: entity.number,
        by=lambda number: number > 0,
    )
    ```

    `actual` (or `_actual` in case of Condition) is optional by the way, so the
    following is also valid:

    ```python
    has_positive_number = Match(
        'has positive number',
        by=lambda entity: entity.number > 0,
    )
    ```

    #### Match over Condition for readability

    If you find passing optional `actual` and mandatory `by` better
    than passing 2nd positional argument as Pass|Fail-function condition,
    and the `Condition` term is too low level for your case, consider using the
    [`Match`][selene.core.condition.Match] subclass in full power. It also fits better
    with a `should` method of Selene entities in context of inline definition
    of conditions – compare: `entity.should(Match(...))` to
    `entity.should(Condition(...))`😉.

    #### Tuning error message description of the actual result

    Remember, that it's not mandatory to wrap lambdas into Query objects
    here to achieve readable error messages, because we already provided a
    custom name. But in case of providing actual that has a readable name,
    e.g. via wrapping as `Query('named', lambda entity: ...)`, we will get
    a bit more descriptive actual result description in the error message:
    `actual named: ...` over `actual: ...` if we provided pure lambda...

    Another way to tune the description of the actual result is to set the
    `_describe_actual_result` parameter. Compare:

    ```python
    has_positive_number = Match(
        'has positive number',
        actual=lambda entity: entity.number,
        by=lambda number: number > 0,
    )
    has_positive_number(0)
    # will fail with:
    '''
    ConditionMismatch: actual: 0
    '''
    ```

    or:

    ```python
    has_positive_number = Match(
        'has positive number',
        actual=Query('number', lambda entity: entity.number),
        by=lambda number: number > 0,
    )
    has_positive_number(0)
    # will fail with:
    '''
    ConditionMismatch: actual number: 0
    '''
    ```

    to:

    ```python
    has_positive_number = Match(
        'has positive number',
        actual=Query('number', lambda entity: entity.number),
        by=lambda number: number > 0,
        _describe_actual_result=lambda number: (
            f'actual number {number} is not positive ❌'
        ),
    )
    has_positive_number(0)
    # will fail with:
    '''
    ConditionMismatch: actual number 0 is not positive ❌
    '''
    ```
    """

    @classmethod
    def by_and(cls, *conditions):
        # TODO: consider refactoring to be predicate-based or both-based
        #      and ensure inverted works
        def func(entity):
            for condition in conditions:
                condition.__call__(entity)

        return cls(' and '.join(map(str, conditions)), func)

    @classmethod
    def by_or(cls, *conditions):
        # TODO: consider refactoring to be predicate-based or both-based
        #      and ensure inverted works
        def func(entity):
            errors: List[Exception] = []
            for condition in conditions:
                try:
                    condition.__call__(entity)
                    return
                except Exception as e:
                    errors.append(e)
            raise AssertionError('; '.join(map(str, errors)))

        return cls(' or '.join(map(str, conditions)), func)

    @classmethod
    def for_each(cls, condition) -> Condition[Iterable[E]]:
        # TODO: consider refactoring to be predicate-based or both-based
        #      and ensure inverted works
        def func(entity):
            items_with_error: List[Tuple[str, str]] = []
            index = None
            for index, item in enumerate(entity):
                try:
                    condition.__call__(item)
                except Exception as error:
                    items_with_error.append((str(item), str(error)))
            if items_with_error:
                raise AssertionError(
                    f'Not matched elements among all with indexes from 0 to {index}:\n'
                    + '\n'.join(
                        [f'{item}: {error}' for item, error in items_with_error]
                    )
                )

        return typing.cast(Condition[Iterable[E]], cls(f' each {condition}', func))

    @classmethod
    def as_not(
        cls,
        condition: Condition[E],
        name: Optional[str] = None,
        /,
        # todo: consider adding additional description param for backwards compatibility
    ) -> Condition[E]:
        return cls(name, condition.not_) if name is not None else condition.not_

    # todo: should we rename this description to name too?
    #       currently it was left as it is for backwards compatibility
    #       but we also can provide keyword arg for b.c.
    #       yet naming first positionally param as name
    @classmethod
    def raise_if_not(cls, description: str, predicate: Predicate[E]) -> Condition[E]:
        return cls(description, _by=predicate)

    @classmethod
    def raise_if_not_actual(
        cls, description: str, query: Lambda[E, R], predicate: Predicate[R]
    ) -> Condition[E]:
        return cls(description, _actual=query, _by=predicate)

    @overload
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        test: Lambda[E, None],
        /,
        *,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    # @overload
    # def __init__(
    #     self,
    #     name: str | Callable[[E | None], str],
    #     *,
    #     by: Tuple[Lambda[E, R], Predicate[R]],
    #     _inverted=False,
    # ): ...

    @overload
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        /,
        *,
        _actual: Lambda[E, R],
        _by: Predicate[R],
        _describe_actual_result: Lambda[R, str] | None = None,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        /,
        *,
        _by: Predicate[E],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    # todo: CONSIDER: accepting tuple of three as name
    #       where three are (prefix, core, suffix),
    #       where each can be substituted with ... (Ellipsis)
    #       signifying that the "default" should be used
    # todo: should we make the name type as Callable[[Condition], str]
    #       instead of Callable[[], str]...
    #       to be able to pass condition itself...
    #       when we pass in child classes we pass self.__str__
    #       that doesn't need to receive self, it already has it
    #       but what if we want to pass some crazy lambda for name from outside
    #       to kind of providing a "name self-based strategy" for condition?
    #       maybe at least we can define it as varagrs? like Callable[..., str]
    #       – we don't need it anymore, case we made it based on entity ;)
    # todo: consider accepting actual and by as Tuples
    #       where first is name for query and second is query fn
    def __init__(
        self,
        name: str | Callable[[E | None], str],  # TODO: consider Callable[[...], str]
        test: Lambda[E, None] | None = None,
        /,  # moved after test to not bother about best name (e.g. test vs match) for now
        *,
        _actual: Lambda[E, R] | None = None,
        # TODO: shouldn't it be by: Predicate[E] | Predicate[R] | None = None ?
        _by: Predicate[R] | None = None,
        _describe_actual_result: Lambda[R, str] | None = None,
        _inverted=False,
        # todo: should we find more "human-readable" name? like in Wait(at_most) over Wait(timeout)
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        # can be already stored
        self.__name = name
        self.__inverted = _inverted
        self.__falsy_exceptions = _falsy_exceptions
        self.__by = None

        if _by:  # i.e. condition is based on predicate (fn returning True/False)
            if test:
                raise ValueError(
                    'either test or by with optional actual should be provided, '
                    'not both'
                )
            self.__actual = _actual
            self.__describe_actual_result = _describe_actual_result
            self.__by = _by
            self.__test = (
                ConditionMismatch._to_raise_if_not(
                    self.__by,
                    self.__actual,
                    _describe_actual_result=self.__describe_actual_result,
                    _falsy_exceptions=_falsy_exceptions,
                )
                if self.__actual
                else ConditionMismatch._to_raise_if_not(
                    self.__by,
                    _falsy_exceptions=_falsy_exceptions,
                )
            )
            self.__test_inverted = (
                ConditionMismatch._to_raise_if_actual(
                    self.__actual,
                    self.__by,
                    _describe_actual_result=self.__describe_actual_result,
                    _falsy_exceptions=_falsy_exceptions,
                )
                if self.__actual
                else ConditionMismatch._to_raise_if(
                    self.__by,
                    _falsy_exceptions=_falsy_exceptions,
                )
            )
            return

        if test:  # i.e. condition based on fn passing with None or raising Error
            if _actual:
                raise ValueError(
                    'either test or by with optional actual should be provided, '
                    'not both'
                )

            self.__test = test

            def as_inverted(entity: E) -> None:
                try:
                    test(
                        entity
                    )  # called via test, not self.__test to make mypy happy :)
                # todo: ensure covered with tests (we might not have the ones)
                except Exception as reason:
                    is_falsy = any(
                        isinstance(reason, exception) for exception in _falsy_exceptions
                    )
                    if is_falsy:
                        return
                    raise reason
                raise ConditionMismatch()

            self.__test_inverted = as_inverted
            return

        raise ValueError(
            'either test or by with optional actual should be provided, not nothing'
        )

    # todo: rethink not_ naming...
    #       if condition is builder-like, for example:
    #       have.text('foo').ignore_case
    #       then, while semi-ok here:
    #       have.text('foo').ignore_case.not_
    #       it becomes totally confusing here:
    #       have.text('foo').not_.ignore_case
    #       but we can reduce incorrect usage just by limiting to -> Condition[E]
    #       – is it enough?
    # todo: decide on actual returned class object...
    #       if we return self.__class__(...), we can technically access new custom
    #       methods in subclasses – condition.not_.HERE
    #       But then we have to override each time the .not_ prop in subclasses
    #       because its impl is based on __init__ and each subclass,
    #       usually, has its own init...
    #       If we return Condition[E](...), we can skip overriding .not_ in subclasses,
    #       but then we can't access new custom methods in subclasses
    #       – condition.not_.HERE
    #       What would be the best for us?
    #       probably an argument for return Condition[E](...) is that
    #       other a bit similar to .not_ methods – or_, and_, each – they can't return
    #       return self.__class__(...) because it does not make sens at all
    #       to call new custom methods of subclasses for the result...
    #       actually calling something after .not_ will also confuse in a lot
    #       of scenarios like in condition.not_.ignore_case – what do we negate here?
    #       – condition? or ignore_case? so seems like best choice
    #       is to return Condition[E](...) here...
    #       But then we also have to ensure, that in not_.* conditions,
    #       we can't use .not_ but have to use _inverted=True) instead
    @property
    def not_(self) -> Condition[E]:
        return (
            Condition(
                self.__name,
                self.__test,
                _inverted=not self.__inverted,
                _falsy_exceptions=self.__falsy_exceptions,
            )
            if not self.__by
            else (
                Condition(
                    self.__name,
                    _actual=self.__actual,  # type: ignore
                    _by=self.__by,
                    _describe_actual_result=self.__describe_actual_result,
                    _inverted=not self.__inverted,
                    _falsy_exceptions=self.__falsy_exceptions,
                )
            )
        )

    def __describe(self, _entity: E | None = None) -> str:
        return self.__name if not callable(self.__name) else self.__name(_entity)

    def __describe_inverted(self, _entity: E | None = None) -> str:
        condition_words = self.__describe(_entity).split(' ')
        is_or_have = condition_words[0]
        if is_or_have not in ('is', 'has', 'have'):
            return f'not ({self.__describe(_entity)})'
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        return f'{is_or_have} {no_or_not} ({name})'

    # todo: consider changing has to have on the fly for CollectionConditions
    # todo: or changing in collection locator rendering `all` to `collection`
    def __str__(self):
        # return self.__describe() if not self.__inverted else self.__describe_inverted()
        return self._name_for()

    # todo: finalize method name (see _typing_functions._SupportsNameForEntity protocol)
    #       should even be a method? or just a property with callable?
    #       hm, probably yes, it should be a method to eliminate branching on usage
    #       while on init we can accept param that can be str or callable
    #       but when coming to final action - it should be always a method call
    #       though, we still can implement it as a property returning callable
    #       but kind of... what for? seems like for no any benefit...
    #       ok... let's think on naming... is the following good? –
    #       condition.describe(entity) - ?
    #       in fact condition does not describe entity, it's more an entity describing condition
    #       ok, other options:
    #       - condition.described_by(entity)
    #       - condition.describe_for(entity)
    #       - condition.description_for(entity)  # + descriptive! emphasize that it is human readable
    #       - condition.name_for(entity)  # + concise! correlate with name param on init
    #       - condition.repr_for(entity)  # + correlate with __repr__ over __str__; + concise; - weird shortcut
    #       - condition.for(entity)  # - looks like a builder
    #         # to remember entity so condition can be .__call__() later without passing entity
    def _name_for(self, entity: E | None = None) -> str:
        return (
            self.__describe(entity)
            if not self.__inverted
            else self.__describe_inverted(entity)
        )

    # todo: we already have entity.matching for Callable[[E], bool]
    #       is it a good idea to use same term for Callable[[E], None] raising error?
    #       but is match vs matchING distinction clear enough?
    #       like "Match it!" says "execute the order!"
    #       and "Matching it?" says "give an answer (True/False) is it matched?"
    #       should we then add one more method to distinguish them? self.matching?
    #       or self.is_matched? (but this will contradict with entity.matching)
    #       still, self.match contradicts with pattern.match(string) that does not raise
    # todo: would a `test` be a better name?
    #       kind of test term relates to testing in context of assertions...
    #       though naturally it does not feel like "assertion"...
    #       more like "predicate" returning bool (True/False), not raising exception
    # TODO: given named as test (or match, etc.)... what if we allow users to do asserts in Selene
    #       that are kind of "classic assertions", i.e. without waiting built in...
    #       then it may look something like this:
    #       > from selene import browser
    #       > from selene.core import match as assert_
    #       > ...
    #       > browser.element('input').clear()
    #       > assert_.blank.test(browser.element('input'))
    #       > # OR:
    #       > assert_.blank.match(browser.element('input'))
    #       > # OR:
    #       > assert_.blank.matches(browser.element('input'))
    #       > # OR:
    #       > assert_.blank.matching(browser.element('input'))
    #       > # OR:
    #       > assert_.blank(browser.element('input'))  #->❤️
    #       hm... what about simply:
    #       > from selene import browser
    #       > from selene.core import match
    #       > ...
    #       > browser.element('input').clear()
    #       > match.blank(browser.element('input'))    #->❤️
    #       this looks also ok:
    #       > from selene import browser
    #       > from selene.core import match as expect
    #       > ...
    #       > browser.element('input').clear()
    #       > expect.blank(browser.element('input'))   #->❤️
    #       TODO: at least, we have to document  – the #->❤️-marked recipes...
    #       hm... but what if condition has param:
    #       > expect.value('foo')(browser.element('input'))
    #       – now it looks less natural
    #       let's compare other options:
    #       > expect.value('foo').test(browser.element('input'))
    #       > expect.value('foo').match(browser.element('input'))
    #       > assert_.value('foo').test(browser.element('input'))
    #       > assert_.value('foo').match(browser.element('input'))
    #       > match.value('foo').match(browser.element('input'))
    #       > match.value('foo').test(browser.element('input'))
    #       what if we add on property returning just self?
    #       or as an method alias to __call__()
    #       > match.value('foo').on(browser.element('input'))
    def _test(self, entity: E) -> None:
        # currently refactored to be alias to __call__ to be in more compliance
        # with some subclasses implementations, that override __call__
        return self.__call__(entity)

    # todo: while `visible.matching(element)` looks good, `match.visible._matching(element)` looks worse
    #       What if we make `match.visible.for_(element)` to serve as predicate in bool context?"
    #       > if match.visible.for_(element): ...
    #       isn't it the perfect design? :)
    def _matching(self, entity: E) -> bool:
        return self.predicate(entity)

    def __call__(self, entity: E) -> None:
        return (
            self.__test(entity) if not self.__inverted else self.__test_inverted(entity)
        )

    def call(self, entity: E) -> None:
        warnings.warn(
            'condition.call(entity) is deprecated,'
            ' use condition(entity) or condition.__call__(entity) instead',
            DeprecationWarning,
        )
        self.__call__(entity)

    @property
    def predicate(self) -> Lambda[E, bool]:
        # counts inversion...
        def fn(entity):
            try:
                self.__call__(entity)  # <- HERE
                return True
            except self.__falsy_exceptions:
                return False

        return fn

    # --- Condition builders (via self) ---

    def and_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_and(self, condition)

    def or_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_or(self, condition)

    @property
    def each(self) -> Condition[Iterable[E]]:
        return Condition.for_each(self)


class Match(Condition[E], Generic[E]):
    """A subclass-based alternative to [Condition][selene.core.condition.Condition]
    class for better readability on straightforward usage of conditions
    built inline with optional custom name, True|False-predicate as `by` argument
    instead of Pass|Fail-function-based condition as 2nd positional Condition argument,
    and optional callable query on entity as `actual` argument to get a value
    from entity to match in `by` callable.

    ### Demo examples

    Example of full inline definition:

    ```python
    from selene import browser
    from selene.core.condition import Match

    ...
    browser.should(Match('title «Expected»', by=lambda its: its.title == 'Expected'))
    ```

    Example of inline definition with reusing existing queries and predicates
    and autogenerated name:

    ```python
    from selene import browser, query
    from selene.core.condition import Match
    from selene.common import predicate

    ...
    browser.should(Match(query.title, predicate.equals('Expected'))
    ```

    !!! warning

        Remember that in most cases you don't need to build condition
        from scratch. You can reuse the ones from predefined conditions
        at `match.*` or among corresponding aliases at `be.*` and `have.*`.
        For example, instead of
        `Match(query.title, predicate.equals('Expected')`
        you can simply reuse `have.title('Expected')` with import
        `from selene import have`.

    Now, let's go in details through different scenarios of constructing
    a Match condition-object.

    ### Differences from Condition initializer

    Unlike its base class (Condition),
    the `Match` subclass has a bit different parameter variations to set
    on constructing new condition. The `Match` initializer:

    - does not accept `test` param (2nd positional-only Condition init parameter),
        that is actually the core of its superclass `Condition` logic,
        and is used to store the Pass|Fail-function (aka functional condition)
        to test the entity against the actual condition criteria,
        implemented in that function.
    - accepts the alternative to `test` params:
        the `by` predicate and the optional `actual` query
        to transform an entity before passing to the predicate for match.
        Both `by` and `actual` are not marked as "experimental" or "internal",
        as they are in case of Condition initializer for now.
        - `by` is a "keyword-only" parameter.
        - `actual` can be passed as a 2nd positional param, if both `name` and `by`
            are present, or as a keyword-only param otherwise.
    - accepts name as the first positional param only, similar to Condition class
        initializer, but can be skipped if you are OK with automatically generated name
        based on `by` and `actual` arguments names.
    - accepts other not mentioned yet parameters, similar to Condition initializer:
        `_describe_actual_result`, `_inverted`, `_falsy_exceptions`.

    ### Better fit for straightforward inline usage

    Such combination of params is especially handy when you build conditions inline
    without the need to store and reuse them later, like in:

    ```python
    from selene import browser
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(
        'normalized value',
        by=lambda it: not re.find_all(r'(\s)\1+', it.locate().get_attribute(value)),
    ))
    ```

    !!! note

        In the example above, it is especially important
        to pass the `'normalized value'` name explicitly,
        because we pass the lambda function in place
        of the `by` predicate argument, and Selene can't autogenerate
        the name for condition based on "anonymous" lambda function.
        The name can be autogenerated only from: regular named function,
        a callable object with custom `__str__` implementation
        (like `Query(name, fn)` object).

    ### Reusing Selene's predefined queries

    To simplify the code a bit, you can reuse the predefined Selene query
    inside the predicate definition:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(
        'normalized value',
        by=lambda element: not re.find_all(r'(\s)\1+', query.value(element)),
    ))
    ```

    Or reusing query outside of predicate definition:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(
        'normalized value',
        actual=query.value,
        by=lambda value: not re.find_all(r'(\s)\1+', value),
    ))
    ```

    In such specific case you can pass actual as a 2nd positional param
    (not a keyword param):

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(
        'normalized value',
        query.value,
        by=lambda value: not re.find_all(r'(\s)\1+', value),
    ))
    ```

    ### Optionality of name

    You can skip first name positional-only parameter to get a default name, that
    will be autogenerated based on passed query name:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(
        actual=query.value,
        by=Query('is normalized', lambda value: not re.find_all(r'(\s)\1+', value)),
    ))
    ```

    ### Reusing custom queries and predicates

    So, if we already have somewhere a helper:

    ```python
    is_normalized = Query('is normalized', lambda value: not re.find_all(r'(\s)\1+', value))

    # or even...
    # (in case of regular named function the 'is normalized' name
    # will be generated from function name):

    def is_normalized(value):
        return not re.find_all(r'(\s)\1+', value)
    ```

    – then we can build a condition on the fly with reusable query-blocks like:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    input = browser.element('#field')
    input.should(Match(actual=query.value, by=is_normalized))
    ```

    !!! warning

        Remember, that we can't use positional arguments for `actual` and `by`
        like in:

        ```python
        from selene import browser, query
        from selene.core.condition import Match

        browser.element('#field').should(Match(query.value, is_normalized))  # ❌
        ```

        This example is not valid!

        Yet it is pretty tempting syntax to have, so maybe we'll implement it
        in future versions, stay tuned;)

    ### Parametrized predicates

    In case you need something "more parametrized":

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    browser.element('#field').should(
        Match(actual=query.value, by=has_no_pattern(r'(\s)\1+'))
    )
    ```

    – where:

    ```python
    import re

    def has_no_pattern(regex):
        return lambda actual: not re.find_all(regex, actual)
    ```

    ### When custom name over autogenerated

    – But now the autogenerated name (that you will see in error messages on fail) –
    may be too low level. Thus, you might want to provide more high level custom name:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    browser.element('#field').should(
        Match('normalized value', query.value, by=has_no_pattern(r'(\s)\1+'))
    )
    ```

    Everything for your freedom of creativity;)

    ### Refactoring conditions for reusability via extending

    At some point of time, you may actually become interested in reusing
    such custom conditions.
    Then you may refactor the last example to something like:

    ```python
    from selene import browser
    from my_project_tests.extensions.selene import have

    browser.element('#field').should(have.normalized_value)
    ```

    – where:

    ```python
    # my_project_tests/extensions/selene/have.py

    from selene.core.condition import Match
    # To reuse all existing have.* conditions, thus, extending them:
    from selene.support.conditions.have import *

    normalized_value = Match(
        'normalized value',
        query.value,
        by=has_no_pattern(r'(\s)\1+')
    )
    ```

    Find more complicated examples of conditions definition in Selene's
    [match.*](../match) module.

    Have fun! ;)
    """

    @overload
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        /,
        actual: Lambda[E, R],
        *,
        by: Predicate[R],
        _describe_actual_result: Lambda[R, str] | None = None,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        /,
        *,
        by: Predicate[E] | Condition[E],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        *,
        actual: Lambda[E, R],
        by: Predicate[R],
        _describe_actual_result: Lambda[R, str] | None = None,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        *,
        by: Predicate[E],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    def __init__(
        self,
        name: str | Callable[[E | None], str] | None = None,
        actual: Lambda[E, R] | None = None,
        *,
        by: Predicate[E] | Predicate[R] | Condition[E],
        _describe_actual_result: Lambda[R, str] | None = None,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        """
        The only valid and stable signatures in usage:

        ```python
        Match(by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', actual=lambda x: x - 1, by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)
        ```

        In addition to the examples above you can optionally add named
        `_describe_actual_result` argument whenever you pass the `actual` argument.
        You also can optionally provide _inverted and _falsy_exceptions arguments.
        But keep in mind that they are marked with `_` prefix to indicate their
        private and potentially "experimental" use, that can change in future versions.
        """
        if not name and not (by_name := Query._full_description_for(by)):
            raise ValueError(
                'either provide a name or ensure that at least by predicate '
                'has __qualname__ (defined as regular named function) '
                'or custom __str__ implementation '
                '(like lambda wrapped in Query object)'
            )
        actual_name = Query._full_description_for(actual)
        name = name or (
            ((str(actual_name) + ' ') if actual_name else '') + str(by_name)  # noqa
        )
        if isinstance(by, Condition):
            super().__init__(
                name,
                by,
                _inverted=_inverted,
                _falsy_exceptions=_falsy_exceptions,
                # Seems like the following is not needed, because by will catch everything internally
                #       – See also unit tests for this case
                # todo: once finalized naming of falsy_exceptions, consider making it protected
                #       for easier access in cases like here...
                # _falsy_exceptions=getattr(
                #     by, f'_{by.__class__.__name__}__falsy_exceptions', _falsy_exceptions
                # ),
            )
        else:
            # todo: fix "cannot infer type of argument 1 of __init__" or ignore
            super().__init__(  # type: ignore
                name,
                _actual=actual,  # type: ignore
                _by=by,
                _describe_actual_result=_describe_actual_result,
                _inverted=_inverted,
                _falsy_exceptions=_falsy_exceptions,
            )

    # TODO: provide examples of error messages

    # TODO: Decide on the *__x methods below
    #       that are actually kind of disabled for now
    @overload
    def __init__x(self, by: Predicate[R]): ...

    @overload
    def __init__x(self, name: str, by: Predicate[R]): ...

    @overload
    def __init__x(self, name: str, actual: Lambda[E, R], by: Predicate[R]): ...

    @overload
    def __init__x(self, *, name: Callable[[], str], by: Predicate[R]): ...

    @overload
    def __init__x(
        self, *, name: Callable[[], str], actual: Lambda[E, R], by: Predicate[R]
    ): ...

    @overload
    def __init__x(self, actual: Lambda[E, R], by: Predicate[R]): ...

    # todo: do we really need such complicated impl in order
    #       to allow passing actual and by as positional arguments?
    #       probably not for now (let's come back after 2.0)...
    #       actual already can be passed as positional in some cases...
    #       and by is pretty concise as it is...
    #       so seems like passing by as positional would not add so much benefits...
    #       though passing actual as positional in some cases (where not it is mandatory)
    #       can make it cleaner... like in:
    #       Match(lambda x: x - 1, by=lambda result: result > 0)
    #       # vs
    #       Match(actual=lambda x: x - 1, by=lambda actual: actual > 0)
    #       yet, the latter is not so bad... even has its benefits...
    # todo: also, take into account that currently the _describe_actual_result
    #       is not counted in the impl below
    def __init__x(self, *args, **kwargs):
        """
        Valid signatures in usage:

        ```python
        # Basic:
        Match(by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', actual=lambda x: x - 1, by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)

        # Extended
        Match(lambda x: x > 0)
        Match(lambda actual: actual - 1, lambda res: res > 0)
        Match('has positive decrement', lambda actual: actual - 1, lambda res: res > 0)
        Match(
            name=lambda: 'has positive decrement',
            actual=lambda actual: actual - 1,
            by=lambda res: res > 0,
        )
        Match(
            name=lambda: 'has positive decrement',
            by=lambda res: res > 0,
        )
        ```
        """
        if not args and kwargs:
            super().__init__(**kwargs)
            return
        if args and isinstance(args[0], str):
            name = args[0]
            left_args = args[1:]
            if not left_args and not kwargs.get('by', None):
                raise ValueError(
                    'lacks by predicate as positional argument or keyword argument'
                )
            if not left_args:
                super().__init__(
                    name, _actual=kwargs.get('actual', None), _by=kwargs['by']
                )
                return
            if left_args and len(left_args) == 1:
                super().__init__(name, _by=left_args[0])
                return
            if left_args and len(left_args) == 2:
                super().__init__(name, _actual=left_args[0], _by=left_args[1])
                return
            raise ValueError('too much of positional arguments')
        if args and callable(args[0]):
            if len(args) + len(kwargs) == 3:
                raise ValueError(
                    'callable name can not be passed as positional argument'
                )
            if len(args) + len(kwargs) == 2:
                actual = args[0]
                by = args[1] if not kwargs else kwargs['by']
            else:
                actual = None
                by = args[0]
            if not (by_name := Query._full_description_for(by)):
                raise ValueError(
                    'either provide name or ensure that at least by predicate'
                    'has __qualname__ (defined as regular named function)'
                    'or custom __str__ implementation '
                    '(like lambda wrapped in Query object)'
                )
            actual_desc = Query._full_description_for(actual)
            name = ((str(actual_desc) + ' ') if actual_desc else '') + str(
                by_name
            )  # noqa
            super().__init__(name, _actual=actual, _by=by)
            return

        raise ValueError('invalid arguments to Match initializer')


def not_(condition_to_be_inverted: Condition):
    return condition_to_be_inverted.not_
