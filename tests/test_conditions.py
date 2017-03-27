from selene.support.conditions import have


def test_condition_have_text():
    assert have.exact_text("text").expected_text == 'text'
    assert have.text("t").expected_text == 't'


def test_condition_have_attr():
    cond = have.attribute("a", "b")
    assert cond.name == "a"
    assert cond.value == "b"


def test_condition_have_css_class():
    assert have.css_class(".css").expected == ".css"


def test_condition_have_size():
    assert have.size(9).expected == 9
    assert have.size_at_least(8).expected == 8


def test_condition_have_exact_texts():
    assert have.exact_texts("a", "b", "c").expected == ("a", "b", "c")


def test_condition_have_texts():
    assert have.texts("a", "b", "c").expected == ("a", "b", "c")
