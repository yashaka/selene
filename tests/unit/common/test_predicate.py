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

from selene.common.predicate import equals_by_contains_to_list


# noinspection PyPep8Naming
class Test__equals_by_contains_to_list:
    def test_same_size(self):
        expected = ['a']
        actual = ['>a<']
        assert equals_by_contains_to_list(expected)(actual)
        assert not equals_by_contains_to_list(actual)(expected)

    def test_expected_list_is_bigger(self):
        expected = ['a', 'b']
        actual = ['>a<']
        assert not equals_by_contains_to_list(expected)(actual)

    def test_expected_list_is_bigger_and_actual_is_empty(self):
        expected = ['a', 'b']
        actual = []
        assert not equals_by_contains_to_list(expected)(actual)

    def test_expected_list_is_smaller(self):
        expected = ['a']
        actual = ['>a<', '>b<']
        assert not equals_by_contains_to_list(expected)(actual)

    def test_expected_list_is_smaller_and_empty(self):
        expected = []
        actual = ['>a<', '>b<']
        assert not equals_by_contains_to_list(expected)(actual)


from selene.common.predicate import equals_to_list


# noinspection PyPep8Naming
class Test__equals_to_list:
    def test_same_size(self):
        expected = ['a', 'b']
        actual = ['a', 'b']
        assert equals_to_list(expected)(actual)

    def test_same_size_and_empty(self):
        expected = []
        actual = []
        assert equals_to_list(expected)(actual)

    def test_expected_list_is_bigger(self):
        expected = ['a', 'b']
        actual = ['a']
        assert not equals_to_list(expected)(actual)

    def test_expected_list_is_bigger_and_actual_is_empty(self):
        expected = ['a']
        actual = []
        assert not equals_to_list(expected)(actual)

    def test_expected_list_is_smaller(self):
        expected = ['a']
        actual = ['a', 'b']
        assert not equals_to_list(expected)(actual)

    def test_expected_list_is_smaller_and_empty(self):
        expected = []
        actual = ['a']
        assert not equals_to_list(expected)(actual)
