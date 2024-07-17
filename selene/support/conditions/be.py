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
from selene.core import match
from selene.support.conditions import not_ as __not

not_ = __not

present_in_dom = match.present_in_dom
in_dom = match.present_in_dom  # TODO: do we need both present_in_dom and in_dom?
absent_in_dom = match.absent_in_dom
hidden_in_dom = match.hidden_in_dom
hidden = match.hidden
visible = match.visible

selected = match.selected

enabled = match.enabled
disabled = match.disabled

clickable = match.clickable

blank = match.blank


_empty = match._empty


# --- Deprecated --- #

empty = match.empty
"""Deprecated 'is empty' condition. Use
[size(0)][selene.support.conditions.have.size] instead.
"""


present = match.present
"""Deprecated 'is present' condition. Use
[present_in_dom][selene.support.conditions.be.present_in_dom] instead.
"""

absent = match.absent
"""Deprecated 'is absent' condition. Use
[absent_in_dom][selene.support.conditions.not_.absent_in_dom] instead.
"""

existing = match.existing
"""Deprecated 'is existing' condition. Use
[present_in_dom][selene.support.conditions.be.present_in_dom] instead.
"""
