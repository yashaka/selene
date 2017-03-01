from selene import bys


def css(selector):
    return bys.by_css(selector)


def xpath(selector):
    return bys.by_xpath(selector)


def name(attribute_value):
    return bys.by_name(attribute_value)


def link_text(text):
    return bys.by_link_text(text)


def partial_link_text(text):
    return bys.by_partial_link_text(text)


def text(element_text):
    return bys.by_text(element_text)


def partial_text(element_text):
    return bys.by_partial_text(element_text)


def be_following_sibling():
    return bys.following_sibling()


def be_parent():
    return bys.parent()


def be_first_child():
    return bys.first_child()
