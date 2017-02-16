from selene import conditions


# *** Condition builders ***


def not_(condition_to_be_inverted):
    return conditions.not_(condition_to_be_inverted)


# *** SeleneElement conditions ***


def exact_text(value):
    return conditions.exact_text(value)


def text(partial_value):
    return conditions.text(partial_value)


def attribute(name, value):
    return conditions.attribute(name, value)


def value(val):
    return conditions.value(val)


def css_class(name):
    return conditions.css_class(name)


# *** SeleneCollection conditions ***


def size(size_of_collection):
    return conditions.size(size_of_collection)


def size_at_least(minimum_size_of_collection):
    return conditions.size_at_least(minimum_size_of_collection)


def exact_texts(*values):
    return conditions.exact_texts(*values)


def texts(*partial_values):
    return conditions.texts(*partial_values)


# *** WebDriver conditions ***


def js_returned_true(script_to_return_bool):
    return conditions.JsReturnedTrue(script_to_return_bool)


def title(exact_value):
    return conditions.Title(exact_value)


def title_containing(partial_value):
    return conditions.TitleContaining(partial_value)


def url(exact_value):
    return conditions.Url(exact_value)


def url_containing(partial_value):
    return conditions.UrlContaining(partial_value)
