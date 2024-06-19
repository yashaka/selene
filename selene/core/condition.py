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
    [`ConditionMismatch._to_raise_on_not(predicate)`][selene.core.exceptions.ConditionMismatch._to_raise_on_not])
    and classes ([`Condition`][selene.core.condition.Condition],
    [`Match`][selene.core.condition.Match])
    to build conditions based on predicates. More on their usage below.

## Predefined conditions

### match.\* VS be.\* & have.\*

Usually you don't need to build conditions yourself,
they are predefined for easier reuse.
In Selene, they are predefined in [`match.*`](selene.core.match)
and can be accessed additionally via [`be.*`](selene.support.conditions.be)
and [`have.*`](selene.support.conditions.have) syntax.

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


# Maybe you don't like that in Selene the match.text condition
# tests for entity text by contains and decide to override it:

def text(expected):
    return __selene_match.exact_text(expected)


def partial_text(expected):
    return __selene_match.text(expected)
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

    If you need a more detailed explanation of
    how we "extended" Selene's predefined conditions in the example above,
    look at the
    [How to implement custom advanced commands?][selene.core.command--how-to-implement-custom-advanced-commands]
    article, that explains same pattern for the case of
    extending Selene predefined commands.

## Functional conditions definition

Ok, now, let's go deeper into how to define custom conditions
starting from function-based conditions.

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
    custom conditions in Selene, jump directly to the examples
    of [`Match`](selene.core.condition.Match) usage.
    In case of any doubts on the topic,
    read on this article without skipping any section.

### Pass|Fail-function-based definition

The simplest way to implement a condition is to define a function
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
is_positive(1)  # passes
try:
    is_positive(0)  # fails
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

# imagine that here we created an async operation p
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

But what if we used lambda predicate to define the condition:

```python
from selene.core.exceptions import ConditionMismatch

has_positive_number = ConditionMismatch._to_raise_if_not(
    lambda entity: entity.number > 0
)
```

Then error would be less informative, because lambda is anonymous –
there is no way to build a description for it:

```text
Timed out after 1.0s, while waiting for:
<class 'Storage'>.<function <lambda> at 0x106b5d8b0>
Reason:  ConditionMismatch: actual: 0
```

To fix this, we can provide a description for the lambda
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
by providing descriptions for our lambdas as follows:

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

This is enough for simpler cases,
but what if we want to be able to compose new conditions based on existing ones,
like in:

```
# wait for not negative even number
Wait(Storage, at_most=1.0).for_(has_positive_number.and_(has_even_number).not_)
```

Here comes in rescue the [`Condition`][selene.core.condition.Condition] class
and its [`Match`][selene.core.condition.Match] subclass,
allowing to build such "re-composable" conditions.

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
    and represent the "conditions that can pass or fail when tested against an entity".
    So, once called on some entity of type E
    such condition object should test if the entity matches the condition object,
    and then simply pass if matched or raise AssertionError otherwise.

    ### When to use Condition-object-based definition

    For most cases you don't need this class directly,
    you can simply reuse the conditions predefined in [`match.*`](selene.core.match).

    You will start to need this class when you want to build your own custom conditions
    to use in a specific to your case assertions.
    And even then, it might be enough to use a simpler version of this class –
    its [Match][selene.core.condition.Match] subclass that has smaller bunch of params
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
    as `input.should(Match(query.value, is_normalized))`,
    see [its section][selene.core.condition.Match].

    And for simplest scenarios you may keep it most KISS
    with "Pass|Fail-function-based conditions" or
    "True|False-predicate-based conditions" as described in
    [Functional conditions definition][selene.core.condition--functional-conditions-definition].

    But when you start bothering about reusing existing conditions
    to build new ones on top of them by applying logical `and`, `or`,
    or `not` operators you start to face some limitations...

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
        'has positive number'
        ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )

    has_negative_number_or_zero = has_positive_number.not_
    ```

    !!! note

        If you see
        [ConditionMismatch._to_raise_if_not_actual](selene.core.exceptions.ConditionMismatch._to_raise_if_not_actual)
        for the first time,
        it's similar to
        [ConditionMismatch._to_raise_if_not](selene.core.exceptions.ConditionMismatch._to_raise_if_not),
        but with inverted order of params:
        `ConditionMismatch._to_raise_if_not_actual(number, is_positive)`
        ==
        `ConditionMismatch._to_raise_if_not(is_positive, number)`

    Notice the following ⬇️

    ### Specifics of the Condition-object-based definition

    - It is simply a wrapping functional condition (PASS|FAIL-function-based)
        into a Condition object with custom description.
        Thus, we can use all variations of defining functional conditions
        to define object-oriented ones.
    - Because we provided a custom description
        (`'has positive number'` in the case above), it's not mandatory
        to wrap lambdas into Query objects to achieve readable error messages,
        unlike we had to do for functional conditions.

    ### Customizing description of inverted conditions

    The description of the `has_negative_number_or_zero` will be automatically
    constructed as `'has not (positive number)'`. In case you want custom:

    ```python
    has_positive_number = Condition(
        'has positive number'
        actual=lambda entity: entity.number,
        by=lambda number: number > 0,
    )

    has_negative_number_or_zero = Condition.as_not(  # ⬅️
        'has negative number or zero',  # 💡
        has_positive_number
    )
    ```

    ### Re-composing methods summary

    Thus:

    - to invert condition you use `condition.not_` property
    - to compose conditions by logical `and` you use `condition.and_(another_condition)`
    - to compose conditions by logical `or` you use `condition.or_(another_condition)`

    ### Alternative signatures for Condition class initializer

    Condition class initializer has more than two params (description and functional condition)
    and different variations of valid signatures to use...

    Recall the initial example:

    ```python
    has_positive_number = Condition(
        'has positive number'
        ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )
    ```

    #### The core parameter: **test**

    Let's rewrite it utilizing the named arguments python feature:

    ```python
    has_positive_number = Condition(
        description='has positive number'
        test=ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )
    ```

    #### Parameters: actual and by VS test

    Thus, the functional condition that is the core of object-oriented condition
    – is passed as the `test` argument. In order to remove a bit of boilerplate
    on object-oriented condition definition, there two other
    alternative parameters to the Condition class initializer:
    `actual` and `by` – similar to the parameters of the
    [`Condition._to_raise_if_not_actual`](selene.core.exceptions.ConditionMismatch._to_raise_if_not_actual)
    helper that we use to define functional True|False-predicate-based conditions.

    Compare:

    ```python
    has_positive_number = Condition(
        description='has positive number'
        test=ConditionMismatch._to_raise_if_not_actual(
            lambda entity: entity.number,
            lambda number: number > 0,
        )
    )
    ```

    to:

    ```python
    has_positive_number = Condition(
        'has positive number'
        actual=lambda entity: entity.number,
        by=lambda number: number > 0,
    )
    ```

    `actual` is optional by the way, so the following is also valid:

    ```python
    has_positive_number = Condition(
        'has positive number'
        by=lambda entity: entity.number > 0,
    )
    ```

    !!! tip

        Remember, that it's not mandatory to wrap lambdas into Query objects
        here to achieve readable error messages,
        because we already provided a custom description.

    #### Relation to Match subclass

    If you find passing optional `actual` and mandatory `by` better
    than passing mandatory `test`,
    and the `Condition` term is too low level for your case, consider using the
    [`Match`][selene.core.condition.Match] subclass of the `Condition` class
    that accepts only `actual` and `by` with optional `description` parameters,
    and fits better with a `should` method of Selene entities – compare:
    `entity.should(Match(...))` to `entity.should(Condition(...))`😉.
    """

    @classmethod
    def by_and(cls, *conditions):
        # TODO: consider refactoring to be predicate-based or both-based
        #      and ensure inverted works
        def func(entity):
            for condition in conditions:
                condition.__call__(entity)

        return cls(' and '.join(map(str, conditions)), test=func)

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

        return cls(' or '.join(map(str, conditions)), test=func)

    @classmethod
    def for_each(cls, condition) -> Condition[Iterable[E]]:
        # TODO consider refactoring to be predicate-based or both-based
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

        return typing.cast(Condition[Iterable[E]], cls(f' each {condition}', test=func))

    @classmethod
    def as_not(  # TODO: ENSURE ALL USAGES ARE NOW CORRECT
        cls, condition: Condition[E], description: Optional[str] = None
    ) -> Condition[E]:
        # TODO: how will it work composed conditions?

        # TODO: should we bother? – about "negated inversion via Condition.as_not"
        #       will "swallow" the reason of failure...
        #       because we invert the predicate or test itself, ignoring exceptions
        #       so then when we "recover original exception failure" on negation
        #       we can just recover it to "false" not to "raise reason error"
        if description:
            return (
                cls(
                    # now we provide the new description that counts inversion
                    description,
                    # specifying already an inverted fn
                    test=condition.__test_inverted,
                    # thus, no need to mark condition for further inversion:
                    _inverted=False,
                )
                if condition.__by is None
                else cls(
                    description,
                    # # We have to skip the actual here (re-building it into by below),
                    # # because can't "truthify" its Exceptions when raised on inverted
                    # # TODO: or can we?
                    # actual=condition.__actual,
                    by=Query._inverted(
                        functools.wraps(condition.__by)(
                            lambda entity: condition.__by(  # type: ignore
                                condition.__actual(entity)
                                if condition.__actual
                                else entity
                            )
                        ),
                        _truthy_exceptions=(AssertionError, WebDriverException),
                    ),
                    _inverted=False,
                )
            )
        else:
            return condition.not_

    @classmethod
    def raise_if_not(cls, description: str, predicate: Predicate[E]) -> Condition[E]:
        return cls(description, by=predicate)

    @classmethod
    def raise_if_not_actual(
        cls, description: str, query: Lambda[E, R], predicate: Predicate[R]
    ) -> Condition[E]:
        return cls(description, actual=query, by=predicate)

    @overload
    def __init__(
        self,
        description: str | Callable[[], str],
        test: Lambda[E, None],
        *,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    # @overload
    # def __init__(
    #     self,
    #     description: str | Callable[[], str],
    #     *,
    #     by: Tuple[Lambda[E, R], Predicate[R]],
    #     _inverted=False,
    # ): ...

    @overload
    def __init__(
        self,
        description: str | Callable[[], str],
        *,
        actual: Lambda[E, R],
        by: Predicate[R],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        description: str | Callable[[], str],
        *,
        by: Predicate[E],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    # todo: CONSIDER: accepting tuple of three as description
    #       where three are (prefix, core, suffix),
    #       where each can be substituted with ... (Ellipsis)
    #       signifying that the "default" should be used
    # TODO: should we make the description type as Callable[[Condition], str]
    #       instead of Callable[[], str]...
    #       to be able to pass condition itself...
    #       when we pass in child classes we pass self.__str__
    #       that doesn't need to receive self, it already has it
    #       but what if we want to pass some crazy lambda for description from outside
    #       to kind of providing a "description self-based strategy" for condition?
    #       maybe at least we can define it as varagrs? like Callable[..., str]
    # TODO: consider accepting actual and by as Tuples
    #       where first is name for query and second is query fn
    def __init__(
        self,
        description: str | Callable[[], str],
        test: Lambda[E, None] | None = None,
        *,
        actual: Lambda[E, R] | None = None,
        by: Predicate[R] | None = None,
        _inverted=False,
        # TODO: better name for _falsy_exceptions?
        #       falsy means that it will become true on inverted
        #       i.e. such exceptions if inverted, will be considered as "truthy"
        #       the problem with such name is that if _inverted=False
        #       then any exception is a False in context of condition behavior,
        #       that simply throw an error as Falsy behavior
        #       maybe then better name would be:
        #       _truthy_exceptions_on_inverted = (AssertionError,)
        #       or
        #       _pass_on_inverted_when = (AssertionError,)
        #       or
        #       _pass_on_inverted_when = (AssertionError,)
        #       hm... but maybe, we actually would want to keep _falsy_exceptions
        #       but make it more generous... i.e. not throwing ConditionMismatch
        #       on any error that is not "falsy"... Make the logic the following:
        #       if error is in _falsy_exceptions, then raise ConditionMismatch
        #       (or pass on inverted)
        #       else just pass the error through... This will give an opportunity
        #       to decide whether to ignore some non-condition-mismatch errors
        #       inside wait.for_ ...
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        # can be already stored
        self.__description = description
        self.__inverted = _inverted
        self.__falsy_exceptions = _falsy_exceptions
        self.__by = None

        if by:  # i.e. condition is based on predicate (fn returning True/False)
            if test:
                raise ValueError(
                    'either test or by with optional actual should be provided, '
                    'not both'
                )
            self.__actual = actual
            self.__by = by
            self.__test = (
                ConditionMismatch._to_raise_if_not(self.__by, self.__actual)
                if self.__actual
                else ConditionMismatch._to_raise_if_not(self.__by)
            )
            self.__test_inverted = (
                ConditionMismatch._to_raise_if_actual(
                    self.__actual,
                    self.__by,
                    # TODO: should we DI? – remove this tight coupling to WebDriverException?
                    #       here and elsewhere
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
            if actual:
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
                except Exception:  # TODO: should we check only AssertionError here?
                    return
                raise ConditionMismatch()

            self.__test_inverted = as_inverted
            return

        raise ValueError(
            'either test or by with optional actual should be provided, not nothing'
        )

    # TODO: rethink not_ naming...
    #       if condition is builder-like, for example:
    #       have.text('foo').ignore_case
    #       then, while semi-ok here:
    #       have.text('foo').ignore_case.not_
    #       it becomes totally confusing here:
    #       have.text('foo').not_.ignore_case
    #       but we can reduce incorrect usage just by limiting to -> Condition[E]
    #       – is it enough?
    # TODO: decide on actual returned class object...
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
                self.__description,
                test=self.__test,
                _inverted=not self.__inverted,
                _falsy_exceptions=self.__falsy_exceptions,
            )
            if not self.__by
            else (
                Condition(
                    self.__description,
                    actual=self.__actual,  # type: ignore
                    by=self.__by,
                    _inverted=not self.__inverted,
                    _falsy_exceptions=self.__falsy_exceptions,
                )
            )
        )

    def __describe(self) -> str:
        return (
            self.__description
            if not callable(self.__description)
            else self.__description()
        )

    def __describe_inverted(self) -> str:
        condition_words = self.__describe().split(' ')
        is_or_have = condition_words[0]
        if is_or_have not in ('is', 'has', 'have'):
            return f'not ({self.__describe()})'
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        return f'{is_or_have} {no_or_not} ({name})'

    # TODO: consider changing has to have on the fly for CollectionConditions
    # TODO: or changing in collection locator rendering `all` to `collection`
    def __str__(self):
        return self.__describe() if not self.__inverted else self.__describe_inverted()

    # TODO: we already have entity.matching for Callable[[E], bool]
    #       is it a good idea to use same term for Callable[[E], None] raising error?
    #       but is match vs matchING distinction clear enough?
    #       like "Match it!" says "execute the order!"
    #       and "Matching it?" says "give an answer (True/False) is it matched?"
    #       should we then add one more method to distinguish them? self.matching?
    #       or self.is_matched? (but this will contradict with entity.matching)
    #       still, self.match contradicts with pattern.match(string) that does not raise
    # TODO: would a `test` be a better name?
    #       kind of test term relates to testing in context of assertions...
    #       though naturally it does not feel like "assertion"...
    #       more like "predicate" returning bool (True/False), not raising exception
    def _test(self, entity: E) -> None:
        # currently refactored to be alias to __call__ to be in more compliance
        # with some subclasses implementations, that override __call__
        return self.__call__(entity)

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
            # TODO: should we check only for AssertionError here? or broader?
            except AssertionError:
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


# TODO: should Match be not just alias but a subclass overriding __init__
#       to accept only description (maybe optional) + predicates with optional actual
#       i.e. not accepting test param at all...
#       as, finally, the test param is more unhandy in straightforward inline usage
#       – So far, YES, it seemed like a good idea to get rid of test param in Match
#       narrowing the usage for the end user to the most convenient one...
#       Hm... but what about redefining conditions based on existing ones?
#       Imagine:
#       $('#save').should(Match('«Save document» is shown', test=be.visible))
#       Such case is rare, and looks like not optimal, because there are better
#       ways to document failures of business steps like this... But maybe...
#       we should at least leave such option...
#       And now we can't pass test to Match... (because of redefined __init__)
#       By the way, something like this would be still possible:
#       $('#save').should(Match('«Save document» is shown', by=query.is_displayed))
#       though, we have no query.is_* so far... should we have?
#       yet... it looks tempting to be able to reuse existing conditions
#       and re-describe them with Match... currently this would be possible only
#       with Condition:
#       $('#save').should(Condition('«Save document» is shown', test=be.visible))
#       maybe this will be important in scenarios like:
#       $('#save').should(Match('clickable', test=be.visible.and_(be.enabled)))
#       or even more relevant not-inline version:
#       clickable = Match('clickable', test=be.visible.and_(be.enabled))
#       though in such case it looks Ok to use Condition class
#       clickable = Condition('clickable', test=be.visible.and_(be.enabled))
#       this will work too right now:
#       clickable = Condition('clickable', be.visible.and_(be.enabled))
#       hm... why not then accept only by in Match (not test), but allow
#       automatic conversion from condition to its predicate
#       when the Condition instance is passed instead of predicate...
#       clickable = Match('clickable', by=be.visible.and_(be.enabled))
#       and then will work too:
#       clickable = Match('clickable', be.visible.and_(be.enabled))
#       hm... looks like a solution...
#       but won't it be overcomplicated in context of understanding?
#       hm... maybe this is really a good idea, because by=condition correlate
#       with all.by(condition)... so it's kind of consistent to expect
#       that condition can be passed in place of by...
#       hm... but won't it be confusing to pass "only predicate" in place of by
#       in the Condition class? o_O
#       It really looks like pretty confusing:D
#       NOTE: if implemented, take into account _falsy_exceptions...
# TODO: just a crazy idea... why then import both Match and/or match.*
#       why not to make match be a class over module –
#       a class with static methods and attributes as predefined conditions
#       and __init__ overriding Condition to accept just predicate & co?
#       TODO: check how autocomplete will work,
#             will it autocomplete after ma... – just match or match()?
#       – Hm, the idea looks very tempting... but we should separate
#       "the most optimal usage" from the one that can tend to be not optimal...
#       If we give an easy way for the end user to to define inline conditions
#       with lambdas - the user may end with doing just that...
#       while in most scenarios it would be better to define custom conditions
#       in a separate Module... Hence, we can complicate it a bit for the user
#       by forcing him to use an additional import of Match
#       to use inline conditions... Hm...
#       But use probably will use be, have, not match... So importing match
#       is already an "another import"... hm...
#       Other thing... is that if we make match a class, then for consistency
#       it would be better to do the same for command.* and query.*...
#       Isn't it too much?
class Match(Condition[E]):
    """A subclass-based alias to [Condition][selene.core.condition.Condition]
    class for better readability on straightforward usage of conditions
    built inline with optional custom description...

    ### Demo examples

    Example of full inline definition:

    ```python
    from selene import browser
    from selene.core.condition import Match

    ...
    browser.should(Match('title «Expected»', by=lambda its: its.title == 'Expected'))
    ```

    Example of inline definition with reusing existing queries and predicates
    and autogenerated description:

    ```python
    from selene import browser, query
    from selene.core.condition import Match
    from selene.common import predicate

    ...
    browser.should(Match(query.title, predicate.equals('Expected'))
    ```

    !!! warning

        Remember that in most cases you don't need to build condition
        from scratch. You can reuse the one from predefined conditions
        at `match.*` or among corresponding aliases at `be.*` and `have.*`.
        For example, instead of
        `Match(query.title, predicate.equals('Expected')`
        you can simply reuse `have.title('Expected')` with import
        `from selene import have`.

    Now, let's go in details through different scenarios of constructing
    a Match condition-object.

    ### Differences from Condition initializer

    Unlike its base class (Condition),
    the `Match` subclass has a bit less of params variations to set
    on constructing new condition.
    The `Match` initializer:

    - does not accept `test` param,
        that is actually the core of its superclass `Condition` logic, and is used to store
        the Pass|Fail-function (aka functional condition) to test the entity
        against the actual condition criteria, implemented in that function.
    - accepts only the alternative to `test` params:
        the `by` predicate and the optional `actual` query
        to transform an entity before passing to the predicate for match.
    - accepts description as the first positional param, but can be skipped
        if you are OK with automatically generated description based on
        `by` and `actual` arguments names or descriptions.

    ### Better fit for straightforward inline usage

    Such combination of params is especially handy
    when you build conditions inline without the need
    to store and reuse them later, like in:

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
        to pass the `'normalized value'` description explicitly,
        because we pass the lambda function in place
        of the `by` predicate argument, and Selene can't autogenerate
        the description for condition based on "anonymous" lambda function.
        The description can be autogenerated only from: regular named function,
        a callable object with custom `__str__` implementation
        (like `Query(description, fn)` object).

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

    ### Optionality of description

    Or with default description, autogenerated based on passed query
    description:

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
    # (in case of regular named function the 'is normalized' description
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

    Or without named arguments for even more concise code:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    browser.element('#field').should(Match(query.value, is_normalized))
    ```

    ### Parametrized predicates

    Or maybe you need something "more parametrized":

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    browser.element('#field').should(Match(query.value, has_no_pattern(r'(\s)\1+')))
    ```

    – where:

    ```python
    import re

    def has_no_pattern(regex):
        return lambda actual: not re.find_all(regex, actual)
    ```

    ### When custom description over autogenerated

    But now the autogenerated description
    (that you will see in error messages on fail) – may be too low level.
    Thus, you might want to provide more high level custom description:

    ```python
    from selene import browser, query
    from selene.core.condition import Match

    browser.element('#field').should(
        Match('normalized value', query.value, has_no_pattern(r'(\s)\1+'))
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

    normalized_value = Match('normalized value', query.value, by=has_no_pattern(r'(\s)\1+'))
    ```

    Have fun! ;)
    """

    # TODO: provide examples of error messages

    # TODO: Decide on the *__x methods below
    #       that are actually kind of disabled for now
    @overload
    def __init__x(self, by: Predicate[R]): ...

    @overload
    def __init__x(self, description: str, by: Predicate[R]): ...

    @overload
    def __init__x(self, description: str, actual: Lambda[E, R], by: Predicate[R]): ...

    @overload
    def __init__x(self, *, description: Callable[[], str], by: Predicate[R]): ...

    @overload
    def __init__x(
        self, *, description: Callable[[], str], actual: Lambda[E, R], by: Predicate[R]
    ): ...

    @overload
    def __init__x(self, actual: Lambda[E, R], by: Predicate[R]): ...

    # TODO: do we really need such complicated impl in order
    #       to allow passing actual and by as positional arguments?
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
            description=lambda: 'has positive decrement',
            actual=lambda actual: actual - 1,
            by=lambda res: res > 0,
        )
        Match(
            description=lambda: 'has positive decrement',
            by=lambda res: res > 0,
        )
        ```
        """
        if not args and kwargs:
            super().__init__(**kwargs)
            return
        if args and isinstance(args[0], str):
            description = args[0]
            left_args = args[1:]
            if not left_args and not kwargs.get('by', None):
                raise ValueError(
                    'lacks by predicate as positional argument or keyword argument'
                )
            if not left_args:
                super().__init__(
                    description, actual=kwargs.get('actual', None), by=kwargs['by']
                )
                return
            if left_args and len(left_args) == 1:
                super().__init__(description, by=left_args[0])
                return
            if left_args and len(left_args) == 2:
                super().__init__(description, actual=left_args[0], by=left_args[1])
                return
            raise ValueError('too much of positional arguments')
        if args and callable(args[0]):
            if len(args) + len(kwargs) == 3:
                raise ValueError(
                    'callable description can not be passed as positional argument'
                )
            if len(args) + len(kwargs) == 2:
                actual = args[0]
                by = args[1] if not kwargs else kwargs['by']
            else:
                actual = None
                by = args[0]
            if not (by_description := Query.full_description_for(by)):
                raise ValueError(
                    'either provide description or ensure that at least by predicate'
                    'has __qualname__ (defined as regular named function)'
                    'or custom __str__ implementation '
                    '(like lambda wrapped in Query object)'
                )
            actual_desc = Query.full_description_for(actual)
            description = ((str(actual_desc) + ' ') if actual_desc else '') + str(
                by_description
            )  # noqa
            super().__init__(description, actual=actual, by=by)
            return

        raise ValueError('invalid arguments to Match initializer')

    @overload
    def __init__(
        self,
        description: str | Callable[[], str],
        actual: Lambda[E, R],
        *,
        by: Predicate[R],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        description: str | Callable[[], str],
        *,
        by: Predicate[E],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ): ...

    @overload
    def __init__(
        self,
        *,
        actual: Lambda[E, R],
        by: Predicate[R],
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

    # TODO: should we rename description to name? won't it confuse with __name__?
    #       probably not, will be actually consistent with __name__...
    def __init__(
        self,
        description: str | Callable[[], str] | None = None,
        actual: Lambda[E, R] | None = None,
        *,
        by: Predicate[E] | Predicate[R],
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        """
        The only valid signatures in usage:

        ```python
        Match(by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', lambda x: x - 1, by=lambda x: x > 0)
        Match('has positive decrement', actual=lambda x: x - 1, by=lambda x: x > 0)
        Match(actual=lambda x: x - 1, by=lambda x: x > 0)
        ```
        """
        if not description and not (by_description := Query.full_description_for(by)):
            raise ValueError(
                'either provide description or ensure that at least by predicate '
                'has __qualname__ (defined as regular named function) '
                'or custom __str__ implementation '
                '(like lambda wrapped in Query object)'
            )
        actual_desc = Query.full_description_for(actual)
        description = description or (
            ((str(actual_desc) + ' ') if actual_desc else '')
            + str(by_description)  # noqa
        )
        # TODO: fix "cannot infer type of argument 1 of __init__" or ignore
        super().__init__(  # type: ignore
            description=description,
            actual=actual,  # type: ignore
            by=by,
            _inverted=_inverted,
            _falsy_exceptions=_falsy_exceptions,
        )


# TODO: clean this temp examples
# is_positive: Match[int] = Match(by=lambda x: x > 0)
# has_positive_decrement: Match[int] = Match(actual=lambda x: x - 1, by=lambda x: x > 0)
# has_positive_decrement_: Match[int] = Match(
#     'has positive decrement', lambda x: x - 1, by=lambda x: x > 0
# )
# has_positive_decrement__: Match[int] = Match(actual=lambda x: x - 1, by=lambda x: x > 0)


# Match(lambda x: x > 0)
# Match(lambda actual: actual - 1, lambda res: res > 0)
# Match('has positive decrement', lambda actual: actual - 1, lambda res: res > 0)
# Match(
#     description=lambda: 'has positive decrement',
#     actual=lambda actual: actual - 1,
#     by=lambda res: res > 0,
# )
# Match(
#     description=lambda: 'has positive decrement',
#     by=lambda res: res > 0,
# )


def not_(condition_to_be_inverted: Condition):
    return condition_to_be_inverted.not_
