from selene.bys import by, by_css, by_name, by_link_text, by_partial_link_text, by_xpath, following_sibling, parent, \
    first_child, by_text, by_partial_text, escape_text_quotes_for_xpath


def test_by_css():
    assert by("a") == ('css selector', 'a')
    assert by_css("span") == ('css selector', 'span')


def test_by_name():
    assert by_name("test") == ('name', 'test')


def test_by_link_text():
    assert by_link_text("text") == ('link text', 'text')


def test_by_partial_link_text():
    assert by_partial_link_text("text") == ("partial link text", "text")


def test_by_xpath():
    assert by_xpath("//a") == ('xpath', "//a")


def test_by_following_sibling():
    assert following_sibling() == ("xpath", './following-sibling::*')


def test_by_parent():
    assert parent() == ("xpath", "..")


def test_first_child():
    assert first_child() == ("xpath", "./*[1]")


def test_by_text():
    assert by_text("test") == ("xpath", './/*[text()[normalize-space(.) = concat("", "test")]]')


def test_by_partial_text():
    assert by_partial_text("text") == ("xpath", './/*[text()[contains(normalize-space(.), concat("", "text"))]]')


def test_by_escape_text_quotes_for_xpath():
    assert escape_text_quotes_for_xpath('test') == 'concat("", "test")'
