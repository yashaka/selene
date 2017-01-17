import ast
from _ast import List
from abc import ABCMeta, abstractmethod
import operator

from future.utils import with_metaclass

from selene.abctypes.conditions import IEntityCondition
from selene.abctypes.webdriver import IWebDriver
from selene.abctypes.webelement import IWebElement
# from selene.elements import SeleneElement, SeleneCollection
from selene.exceptions import ConditionMismatchException


class OrNotToBe(IEntityCondition):

    def description(self):
        return self.__class__.__name__

    def fn(self, entity):
        return entity

or_not_to_be = OrNotToBe


class Not(IEntityCondition):

    def __init__(self, condition):
        # type: (IEntityCondition) -> None
        self._condition = condition

    def description(self):
        return 'not {}'.format(self._condition.description())

    def fn(self, entity):
        try:
            self._condition.fn(entity)
        except Exception as reason:
            return reason
        raise ConditionMismatchException()  # todo: add more information to message

not_ = Not


# *** WebDriver Conditions ***

class WebDriverCondition(with_metaclass(ABCMeta, IEntityCondition)):
    @abstractmethod
    def fn(self, webdriver):
        pass

    def description(self):
        return self.__class__.__name__


class JsReturnedTrue(WebDriverCondition):

    def __init__(self, script_to_return_bool):
        self.script = script_to_return_bool

    def fn(self, webdriver):
        # type: (IWebDriver) -> bool
        result = webdriver.execute_script(self.script)
        if not result:
            raise ConditionMismatchException(
                expected='''script: {script}
                \t\t to return: true'''.format(script=self.script),
                actual='''returned: {result}'''.format(result=result))

js_returned_true = JsReturnedTrue


class Title(WebDriverCondition):

    def __init__(self, text):
        self.expected = text

    def fn(self, webdriver):
        # type: (IWebDriver) -> bool
        actual = webdriver.title.encode('utf-8')
        if not self.expected == actual:
            raise ConditionMismatchException(
                expected=self.expected,
                actual=actual)

title = Title

# *** Element Conditions ***


class ElementCondition(with_metaclass(ABCMeta, IEntityCondition)):

    def description(self):
        return self.__class__.__name__

    def fn(self, element):
        # type: (SeleneElement) -> IWebElement
        return self.match(element.get_actual_webelement())

    @abstractmethod
    def match(self, webelement):
        # type: (IWebElement) -> IWebElement
        pass


def is_matched(condition, webelement):
    # type: (ElementCondition, IWebElement) -> bool
    try:
        condition.match(webelement)
        return True
    except Exception:
        return False


class Visible(ElementCondition):
    def match(self, webelement):
        # type: (SeleneElement) -> IWebElement
        if not webelement.is_displayed():
            raise ConditionMismatchException()
        return webelement


visible = Visible()
appear = visible


class Hidden(ElementCondition):
    def match(self, webelement):
        # type: (SeleneElement) -> IWebElement
        if webelement.is_displayed():
            raise ConditionMismatchException()
        return webelement


hidden = Hidden()
disappear = hidden


# todo: implement as and_(displayed, enabled)
class Clickable(ElementCondition):
    def match(self, webelement):
        # type: (IWebElement) -> IWebElement
        actual_displayed = webelement.is_displayed()
        actual_enabled = webelement.is_enabled()
        if not (actual_displayed and actual_enabled):
            raise ConditionMismatchException(
                expected='displayed and enabled',
                actual='displayed: {displayed}, enabled: {enabled}'.format(
                    displayed=actual_displayed, enabled=actual_enabled))
        return webelement

clickable = Clickable()


class Enabled(ElementCondition):
    def match(self, webelement):
        # type: (SeleneElement) -> IWebElement
        if not webelement.is_enabled():
            raise ConditionMismatchException()
        return webelement

enabled= Enabled()


class InDom(ElementCondition):
    """
    checks if element exist in DOM
    """
    def match(self, webelement):
        return webelement


in_dom = InDom()
exist = in_dom


class Text(ElementCondition):

    def __init__(self, expected_text):
        self.expected_text = expected_text

    def match(self, webelement):
        actual_text = webelement.text.encode('utf-8')
        if self.expected_text not in actual_text:
            raise ConditionMismatchException(expected=self.expected_text, actual=actual_text)
        return webelement

text = Text


class ExactText(ElementCondition):

    def __init__(self, expected_text):
        self.expected_text = expected_text

    def match(self, webelement):
        actual_text = webelement.text.encode('utf-8')
        if not self.expected_text == actual_text:
            raise ConditionMismatchException(expected=self.expected_text, actual=actual_text)
        return webelement

exact_text = ExactText


class CssClass(ElementCondition):

    def __init__(self, expected):
        self.expected = expected

    def match(self, webelement):
        actual = webelement.get_attribute("class")
        if self.expected not in actual.split():
            raise ConditionMismatchException(expected=self.expected, actual='class attribute: {}'.format(actual))
        return webelement

css_class = CssClass


class Attribute(ElementCondition):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def match(self, webelement):
        actual = webelement.get_attribute(self.name)
        if not self.value == actual:
            raise ConditionMismatchException(
                expected='{name}="{value}"'.format(name=self.name, value=self.value),
                actual='{name}="{value}"'.format(name=self.name, value=actual))
        return webelement

attribute = Attribute


def value(val):
    return Attribute('value', val)


blank = value('')


# *** Collection Conditions ***


class CollectionCondition(with_metaclass(ABCMeta, IEntityCondition)):

    def description(self):
        return self.__class__.__name__

    def fn(self, elements):
        # type: (SeleneCollection) -> List[IWebElement]
        return self.match(elements.get_actual_webelements())

    @abstractmethod
    def match(self, webelements):
        # type: (List[IWebElement]) -> List[IWebElement]
        pass


class Texts(CollectionCondition):

    def __init__(self, *expected):
        self.expected = expected

    def match(self, webelements):
        actual = [it.text.encode('utf-8') for it in webelements]
        if not (len(actual) == len(self.expected) and all(map(operator.contains, actual, self.expected))):
            raise ConditionMismatchException(
                expected=self.expected,
                actual=actual)
        return webelements

texts = Texts


class ExactTexts(CollectionCondition):

    def __init__(self, *expected):
        self.expected = expected

    def match(self, webelements):
        actual = [it.text.encode('utf-8') for it in webelements]
        if not (len(actual) == len(self.expected) and all(map(operator.eq, actual, self.expected))):
            raise ConditionMismatchException(
                expected=self.expected,
                actual=actual)
        return webelements

exact_texts = ExactTexts


class Size(CollectionCondition):
    def __init__(self, expected):
        self.expected = expected

    def match(self, webelements):
        actual = len(webelements)
        if not actual == self.expected:
            raise ConditionMismatchException(
                expected=self.expected,
                actual=actual)
        return webelements

size = Size
empty = size(0)


class SizeAtLeast(CollectionCondition):
    def __init__(self, expected):
        self.expected = expected

    def match(self, webelements):
        actual = len(webelements)
        if not actual >= self.expected:
            raise ConditionMismatchException(
                expected='>= {}'.format(self.expected),
                actual=actual)
        return webelements

size_at_least = SizeAtLeast
