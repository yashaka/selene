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
import warnings
from typing import List, Any, Union, Iterable

from selene.common import predicate, helpers
from selene.core import query
from selene.core.condition import Condition
from selene.core.conditions import (
    ElementCondition,
    CollectionCondition,
    BrowserCondition,
)
from selene.core.entity import Collection, Element, Browser

# TODO: consider moving to selene.match.element.is_visible, etc...
element_is_visible: Condition[Element] = ElementCondition.raise_if_not(
    'is visible', lambda element: element().is_displayed()
)


element_is_hidden: Condition[Element] = ElementCondition.as_not(
    element_is_visible, 'is hidden'
)

element_is_enabled: Condition[Element] = ElementCondition.raise_if_not(
    'is enabled', lambda element: element().is_enabled()
)

element_is_disabled: Condition[Element] = ElementCondition.as_not(element_is_enabled)

element_is_clickable: Condition[Element] = element_is_visible.and_(element_is_enabled)

element_is_present: Condition[Element] = ElementCondition.raise_if_not(
    'is present in DOM', lambda element: element() is not None
)

element_is_absent: Condition[Element] = ElementCondition.as_not(element_is_present)

# TODO: how will it work for mobile?
element_is_focused: Condition[Element] = ElementCondition.raise_if_not(
    'is focused',
    lambda element: element()
    == element.config.driver.execute_script('return document.activeElement'),
)


def element_has_text(
    expected: str,
    describing_matched_to='has text',
    compared_by_predicate_to=predicate.includes,
) -> Condition[Element]:
    return ElementCondition.raise_if_not_actual(
        describing_matched_to + ' ' + expected,
        query.text,
        compared_by_predicate_to(expected),
    )


def element_has_exact_text(expected: str) -> Condition[Element]:
    return element_has_text(expected, 'has exact text', predicate.equals)


def element_has_js_property(name: str):
    # TODO: should we keep simpler but less obvious name - *_has_property ?
    def property_value(element: Element) -> str:
        return element().get_property(name)

    def property_values(collection: Collection) -> List[str]:
        return [element.get_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has js property ' + name, property_value, predicate.is_truthy
    )

    class ConditionWithValues(ElementCondition):
        def value(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value '{expected}'",
                property_value,
                predicate.equals(expected),
            )

        def value_containing(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value containing '{expected}'",
                property_value,
                predicate.includes(expected),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values '{expected_}'",
                property_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(str(raw_property_condition), raw_property_condition.call)


def element_has_css_property(name: str):
    def property_value(element: Element) -> str:
        return element().value_of_css_property(name)

    def property_values(collection: Collection) -> List[str]:
        return [element.value_of_css_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has css property ' + name, property_value, predicate.is_truthy
    )

    class ConditionWithValues(ElementCondition):
        def value(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has css property '{name}' with value '{expected}'",
                property_value,
                predicate.equals(expected),
            )

        def value_containing(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has css property '{name}' with value containing '{expected}'",
                property_value,
                predicate.includes(expected),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has css property '{name}' with values '{expected_}'",
                property_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has css property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(str(raw_property_condition), raw_property_condition.call)


def element_has_attribute(name: str):
    def attribute_value(element: Element) -> str:
        return element().get_attribute(name)

    def attribute_values(collection: Collection) -> List[str]:
        return [element.get_attribute(name) for element in collection()]

    raw_attribute_condition = ElementCondition.raise_if_not_actual(
        'has attribute ' + name, attribute_value, predicate.is_truthy
    )

    # TODO: is it OK to have some collection conditions inside a thing named element_has_attribute ? o_O
    class ConditionWithValues(ElementCondition):
        def value(self, expected: str, ignore_case=False) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value '{expected}'",
                attribute_value,
                predicate.equals(expected, ignore_case),
            )

        def value_containing(
            self, expected: str, ignore_case=False
        ) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value containing '{expected}'",
                attribute_value,
                predicate.includes(expected, ignore_case),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values '{expected_}'",
                attribute_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values containing '{expected_}'",
                attribute_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(
        str(raw_attribute_condition), raw_attribute_condition.call
    )


element_is_selected: Condition[Element] = ElementCondition.raise_if_not(
    'is selected', lambda element: element().is_selected()
)


def element_has_value(expected: str) -> Condition[Element]:
    return element_has_attribute('value').value(expected)


def element_has_value_containing(expected: str) -> Condition[Element]:
    return element_has_attribute('value').value_containing(expected)


def collection_has_values(
    *expected: Union[str, Iterable[str]]
) -> Condition[Collection]:
    return element_has_attribute('value').values(*expected)


def collection_has_values_containing(
    *expected: Union[str, Iterable[str]]
) -> Condition[Collection]:
    return element_has_attribute('value').values_containing(*expected)


def element_has_css_class(expected: str) -> Condition[Element]:
    def class_attribute_value(element: Element) -> str:
        return element().get_attribute('class')

    return ElementCondition.raise_if_not_actual(
        f"has css class '{expected}'",
        class_attribute_value,
        predicate.includes_word(expected),
    )


element_is_blank: Condition[Element] = element_has_exact_text('').and_(
    element_has_value('')
)


def element_has_tag(
    expected: str,
    describing_matched_to='has tag',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Element]:
    return ElementCondition.raise_if_not_actual(
        f'{describing_matched_to} + {expected}',
        query.tag,
        compared_by_predicate_to(expected),
    )


def element_has_tag_containing(expected: str) -> Condition[Element]:
    return element_has_tag(expected, 'has tag containing', predicate.includes)


# TODO: should not we make empty to work on both elements and collections?
#   to assert have.size(0) on collections
#   to assert have.value('').and(have.exact_text('')) on element
def _is_collection_empty(collection: Collection) -> bool:
    warnings.warn(
        'match.collection_is_empty or be.empty is deprecated; '
        'use more explicit and obvious have.size(0) instead',
        DeprecationWarning,
    )
    return len(collection()) == 0


collection_is_empty: Condition[Collection] = CollectionCondition.raise_if_not(
    'is empty', _is_collection_empty
)


def collection_has_size(
    expected: int,
    describing_matched_to='has size',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Collection]:
    def size(collection: Collection) -> int:
        return len(collection())

    return CollectionCondition.raise_if_not_actual(
        f'{describing_matched_to} {expected}',
        size,
        compared_by_predicate_to(expected),
    )


def collection_has_size_greater_than(expected: int) -> Condition[Collection]:
    return collection_has_size(
        expected, 'has size greater than', predicate.is_greater_than
    )


def collection_has_size_greater_than_or_equal(
    expected: int,
) -> Condition[Collection]:
    return collection_has_size(
        expected,
        'has size greater than or equal',
        predicate.is_greater_than_or_equal,
    )


def collection_has_size_less_than(expected: int) -> Condition[Collection]:
    return collection_has_size(expected, 'has size less than', predicate.is_less_than)


def collection_has_size_less_than_or_equal(
    expected: int,
) -> Condition[Collection]:
    return collection_has_size(
        expected,
        'has size less than or equal',
        predicate.is_less_than_or_equal,
    )


# TODO: make it configurable whether assert only visible texts or ot
def collection_has_texts(*expected: Union[str, Iterable[str]]) -> Condition[Collection]:
    expected_ = helpers.flatten(expected)

    def visible_texts(collection: Collection) -> List[str]:
        return [
            webelement.text for webelement in collection() if webelement.is_displayed()
        ]

    return CollectionCondition.raise_if_not_actual(
        f'has texts {expected_}',
        visible_texts,
        predicate.equals_by_contains_to_list(expected_),
    )


def collection_has_exact_texts(
    *expected: Union[str, Iterable[str]]
) -> Condition[Collection]:
    expected_ = helpers.flatten(expected)

    def visible_texts(collection: Collection) -> List[str]:
        return [
            webelement.text for webelement in collection() if webelement.is_displayed()
        ]

    return CollectionCondition.raise_if_not_actual(
        f'has exact texts {expected_}',
        visible_texts,
        predicate.equals_to_list(expected_),
    )


# TODO: consider refactoring the code like below by moving outside fns like url, title, etc...
# TODO: probably we will do that nevertheless when reusing "commands&queries" inside element class definitions
def browser_has_url(
    expected: str,
    describing_matched_to='has url',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def url(browser: Browser) -> str:
        return browser.driver.current_url

    return BrowserCondition.raise_if_not_actual(
        f"{describing_matched_to} '{expected}'",
        url,
        compared_by_predicate_to(expected),
    )


def browser_has_url_containing(expected: str) -> Condition[Browser]:
    return browser_has_url(expected, 'has url containing', predicate.includes)


def browser_has_title(
    expected: str,
    describing_matched_to='has title',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def title(browser: Browser) -> str:
        return browser.driver.title

    return BrowserCondition.raise_if_not_actual(
        f"{describing_matched_to} '{expected}'",
        title,
        compared_by_predicate_to(expected),
    )


def browser_has_title_containing(expected: str) -> Condition[Browser]:
    return browser_has_title(expected, 'has title containing', predicate.includes)


def browser_has_tabs_number(
    expected: int,
    describing_matched_to='has tabs number',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def tabs_number(browser: Browser) -> int:
        return len(browser.driver.window_handles)

    return BrowserCondition.raise_if_not_actual(
        f'{describing_matched_to} {expected}',
        tabs_number,
        compared_by_predicate_to(expected),
    )


def browser_has_tabs_number_greater_than(expected: int) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected, 'has tabs number greater than', predicate.is_greater_than
    )


def browser_has_tabs_number_greater_than_or_equal(
    expected: int,
) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected,
        'has tabs number greater than or equal',
        predicate.is_greater_than_or_equal,
    )


def browser_has_tabs_number_less_than(expected: int) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected, 'has tabs number less than', predicate.is_less_than
    )


def browser_has_tabs_number_less_than_or_equal(
    expected: int,
) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected,
        'has tabs number less than or equal',
        predicate.is_less_than_or_equal,
    )


def browser_has_js_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    warnings.warn(
        'deprecated because js does not work for mobile; '
        'use have.script_returned(True, ...) instead',
        DeprecationWarning,
    )

    return browser_has_script_returned(expected, script, *args)


def browser_has_script_returned(
    expected: Any, script: str, *args
) -> Condition[Browser]:
    def script_result(browser: Browser):
        return browser.driver.execute_script(script, *args)

    return BrowserCondition.raise_if_not_actual(
        f'has the ```{script}``` script returned {expected}',
        script_result,
        predicate.equals(expected),
    )
