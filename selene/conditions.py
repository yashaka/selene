from operator import contains, eq
from selene import config

# todo: refactor conditions to accept element.finder, not element - to make implementation of conditions more secure


class Condition(object):

    def __init__(self):
        self.found = None

    def __call__(self, entity):
        self.entity = entity
        self.found = self.entity()  # todo: do we actually need it?
                                    # while we have self.found = wait_for(...
        return self.found if self.apply() else None

    def __str__(self):
            expected_string = str(self.expected()) if (self.expected() is not None) else ""
            actual_string = str(self.actual()) if (self.actual() is not None) else ""
            return """
            for %s found by: %s%s%s
        """ % (self.identity(),
               self.entity,
               """:
            \texpected: """ + expected_string,
               """
            \t  actual: """ + actual_string)

    def identity(self):
        return "element"

    def expected(self):
        return None

    def actual(self):
        return None

    def apply(self):
        return None


class CollectionCondition(Condition):

    def identity(self):
        return "elements"


class text(Condition):
    def __init__(self, expected_text):
        self.expected_text = expected_text
        self.actual_text = None

    def compare_fn(self):
        return contains

    def apply(self):
        self.actual_text = self.found.text.encode('utf-8')
        return self.compare_fn()(self.actual_text, self.expected_text)

    def expected(self):
        return self.expected_text

    def actual(self):
        return self.actual_text


class exact_text(text):
    def compare_fn(self):
        return eq


class Visible(Condition):
    def apply(self):
        return self.found.is_displayed()


visible = Visible()


class Clickable(Condition):
    def apply(self):
        return self.found.is_displayed and self.found.is_enabled()


clickable = Clickable()


class Enabled(Condition):
    def apply(self):
        return self.found.is_enabled()

enabled = Enabled()


# todo: consider renaming it to something else, because in jSelenide exist = visible
class Exist(Condition):
    """
    checks if element exist in DOM
    """
    def apply(self):
        return True


exist = Exist()


class Hidden(Condition):
    def apply(self):
        return not self.found.is_displayed()

hidden = Hidden()

class css_class(Condition):

    def __init__(self, class_attribute_value):
        self.expected_containable_class = class_attribute_value
        self.actual_class = None

    def apply(self):
        self.actual_class = self.found.get_attribute("class")
        return self.expected_containable_class in self.actual_class

    def expected(self):
        return self.expected_containable_class

    def actual(self):
        return self.actual()


#########################
# COLLECTION CONDITIONS #
#########################


class texts(CollectionCondition):

    def __init__(self, *expected_texts):
        self.expected_texts = expected_texts
        self.actual_texts = None

    def compare_fn(self):
        return contains

    def apply(self):
        self.actual_texts = [item.text.encode('utf-8') for item in self.found]
        return len(self.actual_texts) == len(self.expected_texts) and \
            all(map(self.compare_fn(), self.actual_texts, self.expected_texts))

    def expected(self):
        return self.expected_texts

    def actual(self):
        return self.actual_texts


class exact_texts(texts):

    def compare_fn(self):
        return eq

class size(CollectionCondition):

    def __init__(self, expected_size):
        self.expected_size = expected_size
        self.actual_size = None

    def apply(self):
        self.actual_size = len(self.found)
        return self.actual_size == self.expected_size

    def expected(self):
        return self.expected_size

    def actual(self):
        return self.actual_size


empty = size(0)


class size_at_least(CollectionCondition):

    def __init__(self, minimum_size):
        self.minimum_size = minimum_size
        self.actual_size = None

    def apply(self):
        self.actual_size = len(self.found)
        return self.actual_size >= self.minimum_size

    def expected(self):
        return self.minimum_size

    def actual(self):
        return self.actual_size
