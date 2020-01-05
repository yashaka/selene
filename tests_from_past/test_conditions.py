# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
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
