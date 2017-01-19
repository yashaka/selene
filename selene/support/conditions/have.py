from selene import conditions

size = conditions.size
size_at_least = conditions.size_at_least
text = conditions.text
exact_text = conditions.exact_text
texts = conditions.texts
exact_texts = conditions.exact_texts
css_class = conditions.css_class
attribute = conditions.attribute
value = conditions.value
not_ = conditions.not_


def js_returned_true(script_to_return_bool):
    return conditions.JsReturnedTrue(script_to_return_bool)


def title(text):
    return conditions.Title(text)
