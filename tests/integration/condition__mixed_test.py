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
import pytest

from selene import have, be
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage
from tests import const


# todo: consider breaking it down into separate tests


def test_should_match_different_things(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    ss = lambda selector: session_browser.with_(timeout=0.1).all(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        <!--<input id="absent"></li>-->
        <input id="hidden-empty" style="display: none">
        <input id="hidden" style="display: none" value=" One  !!!">
        <input id="visible-empty" style="display: block" value="">
        <input id="visible" style="display: block" value=" One  !!!">
        <!--etc...-->
        <ul>Hey:
           <li><label>First Name:</label> <input type="text" class="name" id="firstname" value="John 20th"></li>
           <li><label>Last Name:</label> <input type="text" class="name" id="lastname" value="Doe 2nd"></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><input type="text" class='exercise' id="pullup" value="20"></li>
           <li><label>Push up:</label><input type="text" class='exercise' id="pushup" value="30"></li>
        </ul>
        '''
    )

    # THEN

    # have texts & co + filtering for visibility via config?

    ss('li#hidden,li#visible').should(match.texts('One'))
    ss('li#hidden,li#visible').should(match._text_patterns(r'[Oo]ne.+'))
    ss('li#hidden,li#visible').should(match._text_patterns_like(r'[Oo]ne.+', [...]))
    ss('li#hidden,li#visible').should(match._texts_like('One', [...]))
    ss('li#hidden,li#visible').should(match.exact_texts('One !!!'))
    ss('li#hidden,li#visible').should(match._exact_texts_like('One !!!', [...]))

    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match.texts('', 'One')
    )
    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match._text_patterns('', r'[Oo]ne.+')
    )
    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match._text_patterns_like('', r'[Oo]ne.+', [...])
    )
    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match._texts_like('', 'One', [...])
    )
    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match.exact_texts('', 'One !!!')
    )
    ss('li#hidden,li#visible').with_(_match_only_visible_elements_texts=False).should(
        match._exact_texts_like('', 'One !!!', [...])
    )

    # have tag?
    # - visible passes
    s('li#visible').should(match.tag('li'))
    s('li#visible').should(have.tag('li'))
    s('input#visible').should(have.no.tag('input').not_)
    s('input#visible').should(have.tag('input').not_.not_)
    # - hidden passes
    s('li#hidden').should(match.tag('li'))
    s('li#hidden').should(have.tag('li'))
    s('input#hidden').should(have.no.tag('input').not_)
    s('input#hidden').should(have.tag('input').not_.not_)
    # have tag containing?
    # - visible passes
    s('li#visible').should(match.tag_containing('l'))
    s('li#visible').should(have.tag_containing('l'))
    s('input#visible').should(have.no.tag_containing('in').not_)
    s('input#visible').should(have.tag_containing('in').not_.not_)
    # - hidden passes
    s('li#hidden').should(match.tag_containing('l'))
    s('li#hidden').should(have.tag_containing('l'))
    s('input#hidden').should(have.no.tag_containing('in').not_)
    s('input#hidden').should(have.tag_containing('in').not_.not_)
    # absent fails with failure
    try:
        s('li#absent').should(have.tag('li'))
        pytest.fail('expect FAILURE')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#absent')).has tag li\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"li#absent"}\n'
        ) in str(error)
    # have no tag?
    s('li#visible').should(have.no.tag('input'))
    s('input#visible').should(have.no.tag('li'))
    # have no tag containing?
    s('li#visible').should(have.no.tag_containing('in'))
    s('input#visible').should(have.no.tag_containing('l'))

    # have title?
    session_browser.should(have.title('Selene Test Page'))
    session_browser.should(have.no.title('Test'))
    # have title containing?
    session_browser.should(have.title_containing('Test'))
    session_browser.should(have.no.title_containing('test'))
    session_browser.should(have.title_containing('test').ignore_case)
    session_browser.with_(_ignore_case=True).should(have.title_containing('test'))


def test_should_have_size__applied_to_collection__passed_and_failed(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    ss = lambda selector: session_browser.with_(timeout=0.1).all(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <h1>My Favorite Books</h1>
        <ul style="list-style-type: square;">
            <li>HPMOR</li>
            <li>Mushoku Tensei</li>
            <li>The Witcher</li>
            <li>Dune</li>
            <li>Game of Thrones</li>
            <li></li>
            <li style="display: none">Cryptonomicon</li>
            <li>Shogun</li>
        </ul>
        '''
    )

    # have size?
    ss('li').with_(_match_only_visible_elements_size=True).should(match.size(7))

    ss('li').should(match.size(8))

    ss('li').should(have.no.size(9))
    ss('li').should(have.size(8))
    ss('li').should(have.no.size(7))

    try:
        ss('li').should(have.size(7))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have size 7\n"
            '\n'
            'Reason: ConditionMismatch: actual: 8\n'
        ) in str(error)

    # have size or less?
    ss('li').should(have.size(9).or_less)
    ss('li').should(have.size(8).or_less)
    try:
        ss('li').should(have.size(7).or_less)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have size 7 or less\n"
            '\n'
            'Reason: ConditionMismatch: actual size: 8\n'
        ) in str(error)
    ss('li').should(have.no.size(7).or_less)
    try:
        ss('li').should(have.no.size(8).or_less)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (  # TODO: fix it because now inversion does not come into action... in context of describing...
            "browser.all(('css selector', 'li')).have no (size 8 or less)\n"
            '\n'
            'Reason: ConditionMismatch: actual size: 8\n'
        ) in str(
            error
        )
    ss('li').should(have.no.size_less_than_or_equal(7))

    # todo: add a few failed cases below...

    # have size or more?
    ss('li').should(have.size(7).or_more)
    ss('li').should(have.size(8).or_more)
    ss('li').should(have.no.size(9).or_more)
    ss('li').should(have.no.size_greater_than_or_equal(9))

    # have size more than
    ss('li').should(have.no.size(8)._more_than)
    ss('li').should(have.no.size_greater_than(8))
    ss('li').should(have.size_greater_than(7))
    ss('li').should(have.size_greater_than(0))

    # have size less than
    ss('li').should(have.size_less_than(9))
    ss('li').should(have.no.size(8)._less_than)
    ss('li').should(have.no.size_less_than(8))
    ss('li').should(have.no.size_less_than(0))


def test_should_have_size__applied_to_browser__passed_and_failed(
    function_browser,
):
    browser = function_browser.with_(timeout=0.1, window_width=720, window_height=480)
    s = lambda selector: browser.element(selector)
    ss = lambda selector: browser.all(selector)
    GivenPage(browser).opened_with_body(
        '''
        <ul>
        <form id="form-no-text-with-values">
            <div id="empty-inputs">
                <input id="hidden-empty" style="display: none">
                <input id="visible-empty" style="display: block" value="">
            </div>
            <div id="non-empty-inputs">
                <input id="hidden" style="display: none" value=" One  !!!">
                <input id="visible" style="display: block" value=" One  !!!">
            </div>
        </form>
        '''
    )

    # browser have size?
    browser.should(have.size({'height': 480, 'width': 720}))
    try:
        browser.should(have.size({'height': 481, 'width': 720}))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.has size {'height': 481, 'width': 720}\n"
            '\n'
            "Reason: ConditionMismatch: actual: {'width': 720, 'height': 480}\n"
        ) in str(error)
    browser.should(have.no.size({'height': 481, 'width': 720}))
    # TODO: add failed inverted case


# todo: make it pass both locally and on CI (on CI the field has different size, why?)
def x_test_should_have_size__applied_to_element__passed_and_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    s = lambda selector: browser.element(selector)
    ss = lambda selector: browser.all(selector)
    GivenPage(browser).opened_with_body(
        '''
        <ul>
        <form id="form-no-text-with-values">
            <div id="empty-inputs">
                <input id="hidden-empty" style="display: none">
                <input id="visible-empty" style="display: block" value="">
            </div>
            <div id="non-empty-inputs">
                <input id="hidden" style="display: none" value=" One  !!!">
                <input id="visible" style="display: block" value=" One  !!!">
            </div>
        </form>
        '''
    )

    # element have size?
    s('input#hidden-empty').should(have.size({'height': 22, 'width': 147}))
    s('input#visible-empty').should(have.size({'height': 22, 'width': 147}))
    try:
        s('input#visible-empty').should(have.size({'height': 21, 'width': 147}))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible-empty')).has size "
            "{'height': 21, 'width': 147}\n"
            '\n'
            "Reason: ConditionMismatch: actual size: {'height': 22, 'width': 147}\n"
            'Screenshot: '
        ) in str(error)
    s('input#visible-empty').should(have.no.size({'height': 21, 'width': 147}))
    s('input#visible-empty').should(have.no.size({'height': 22, 'width': 146}))
    try:
        s('input#visible-empty').should(have.no.size({'height': 22, 'width': 147}))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible-empty')).has no (size "
            "{'height': 22, 'width': 147})\n"
            '\n'
            "Reason: ConditionMismatch: actual size: {'height': 22, 'width': 147}\n"
            'Screenshot: '
        ) in str(error)


def test_should_be_emtpy__applied_to_non_form__passed_and_failed__compared(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    ss = lambda selector: session_browser.with_(timeout=0.1).all(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        <!--<input id="absent"></li>-->
        <form id="form-no-text-with-values">
            <div id="empty-inputs">
                <input id="hidden-empty" style="display: none">
                <input id="visible-empty" style="display: block" value="">
            </div>
            <div id="non-empty-inputs">
                <input id="hidden" style="display: none" value=" One  !!!">
                <input id="visible" style="display: block" value=" One  !!!">
            </div>
        </form>
        <form id="form-with-text-with-values">
            <div id="empty-inputs">
                <input id="hidden-empty-2" style="display: none">
                <label>Visible empty:</label>
                <input id="visible-empty-2" style="display: block" value="">
            </div>
            <div id="non-empty-inputs">
                <input id="hidden-2" style="display: none" value=" One  !!!">
                <label>Visible:</label>
                <input id="visible-2" style="display: block" value=" One  !!!">
            </div>
        </form>
        <!--etc...-->
        <ul>Hey:
           <li><label>First Name:</label> <input type="text" class="name" id="firstname" value="John 20th"></li>
           <li><label>Last Name:</label> <input type="text" class="name" id="lastname" value="Doe 2nd"></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><input type="text" class='exercise' id="pullup" value="20"></li>
           <li><label>Push up:</label><input type="text" class='exercise' id="pushup" value="30"></li>
        </ul>
        '''
    )

    # be empty vs have size vs be blank + inverted?
    ss('.exercise').should(have.size(2))
    ss('.exercise').should(have.no.size(0))
    ss('.exercise').should(be.not_._empty)
    ss('#visible').should(have.size(2))
    ss('#visible').should(have.no.size(0))
    ss('#visible').should(be.not_._empty)
    ss('#hidden').should(have.size(2))
    try:
        ss('#hidden').should(have.size(0))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '#hidden')).have size 0\n"
            '\n'
            'Reason: ConditionMismatch: actual: 2\n'
        ) in str(error)
    try:
        ss('#hidden').should(be._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '#hidden')).is empty\n"
            '\n'
            'Reason: ConditionMismatch: actual size: 2\n'
        ) in str(error)
    try:
        s('input#visible').should(be.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible')).is blank\n"
            '\n'
            'Reason: ConditionMismatch: actual value:  One  !!!\n'
        ) in str(error)
    try:
        s('input#visible').should(be._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible')).is empty\n"
            '\n'
            'Reason: ConditionMismatch: actual value:  One  !!!\n'
        ) in str(error)
    try:
        s('li#visible').should(be.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#visible')).is blank\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    try:
        s('li#visible').should(be._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#visible')).is empty\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    ss('#hidden').should(have.no.size(0))
    ss('#hidden').should(be.not_._empty)
    ss('.absent').should(have.size(0))
    try:
        ss('.absent').should(have.no.size(0))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.absent')).have no (size 0)\n"
            '\n'
            'Reason: ConditionMismatch: actual: 0\n'
        ) in str(error)
    ss('.absent').should(be._empty)
    try:
        ss('.absent').should(be.not_._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.absent')).is not (empty)\n"
            '\n'
            'Reason: ConditionMismatch: actual size: 0\n'
        ) in str(error)
    s('li#visible-empty').should(be.blank)
    s('input#visible-empty').should(be.blank)
    s('li#visible').should(be.not_.blank)
    s('input#visible').should(be.not_.blank)
    s('li#visible-empty').should(be._empty)
    s('input#visible-empty').should(be._empty)
    s('li#visible').should(be.not_._empty)
    s('input#visible').should(be.not_._empty)

    # non-form container elements are considered empty if there is no text inside
    s('#form-no-text-with-values div#empty-inputs').should(be._empty)
    s('#form-no-text-with-values div#non-empty-inputs').should(be._empty)
    s('#form-with-text-with-values div#empty-inputs').should(be.not_._empty)
    s('#form-with-text-with-values div#non-empty-inputs').should(be.not_._empty)


def test_should_be_emtpy__applied_to_form__passed_and_failed(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    ss = lambda selector: session_browser.with_(timeout=0.1).all(selector)
    GivenPage(session_browser.driver).opened_with_body(
        f'''
        <form id="form-with-text-no-values">
            <textarea id="textarea-no-value-no-text"></textarea>
            <input id="no-type-no-value">
            <input id="no-type-explicit-empty-value" value="">

            <input type="text" id="type-text-no-value">
            <input type="text" id="type-text-explicit-empty-value" value="">

            <input type="checkbox" id="type-checkbox-not-checked" name="vehicle1" value="Bike">
            <label for="vehicle1"> I have a bike</label><br>

            <input type="radio" id="type-radio-not-checked" name="fav_language" value="HTML">
            <label for="html">HTML</label><br>

            <select id="select-empty-value">
                <option value=""></option>
                <option value="volvo">Volvo</option>
                <option value="saab">Saab</option>
                <option value="mercedes">Mercedes</option>
                <option value="audi">Audi</option>
            </select>

            <!--button, submit, reset should be not counted:-->
            <button id="button-no-value-with-text">Click me</button>
            <input type="submit" id="type-submit-with-value" value="Submit">
            <input type="reset" id="type-reset-with-value" value="Reset">

            <!--image and hidden should be not counted:-->
            <input type="image" id="type-image-with-src-no-value" src="{const.LOGO_PATH}">
            <input type="hidden" id="type-hidden-some-value" value="some">

            <!--range and color should be not counted
                because they always have at least 0 and #000000
                that can hardly be counted as "empty"-->
            <input type="range" id="type-range-0-value">
            <input type="color" id="type-color-000000-value">
        </form>

        <form id="form-no-text-no-values">
            <textarea id="textarea-no-value-no-text"></textarea>
            <input id="no-type-no-value">
            <input id="no-type-explicit-empty-value" value="">

            <input type="text" id="type-text-no-value">
            <input type="text" id="type-text-explicit-empty-value" value="">

            <input type="checkbox" id="type-checkbox-not-checked" name="vehicle1" value="Bike">

            <input type="radio" id="type-radio-not-checked" name="fav_language" value="HTML">

            <select id="select-empty-value">
                <option value=""></option>
                <option value="volvo">Volvo</option>
                <option value="saab">Saab</option>
                <option value="mercedes">Mercedes</option>
                <option value="audi">Audi</option>
            </select>

            <!--button, submit, reset should be not counted:-->
            <!--<button id="button-no-value-with-text">Click me</button>-->
            <input type="submit" id="type-submit-with-value" value="Submit">
            <input type="reset" id="type-reset-with-value" value="Reset">

            <!--image and hidden should be not counted:-->
            <input type="image" id="type-image-with-src-no-value" src="{const.LOGO_PATH}">
            <input type="hidden" id="type-hidden-some-value" value="some">

            <!--range and color should be not counted
                because they always have at least 0 and #000000
                that can hardly be counted as "empty"-->
            <input type="range" id="type-range-0-value">
            <input type="color" id="type-color-000000-value">
        </form>

        <form id="form-no-text-with-values">
            <textarea id="textarea-with-value-no-text"></textarea> <!-- value will be set via UI -->
            <input id="no-type-with-value" value="no-type-with-value;">
            <input id="no-type-explicit-empty-value" value="">

            <input type="text" id="type-text-with-value" value="type-text-with-value;">
            <input type="text" id="type-text-explicit-empty-value" value="">

            <input type="checkbox" id="type-checkbox-checked" name="vehicle1" value="Bike" checked>

            <input type="radio" id="type-radio-checked" name="fav_language" value="HTML" checked>

            <select id="select-empty-value">
                <!--<option value=""></option>-->
                <option value="volvo">Volvo</option>
                <option value="saab">Saab</option>
                <option value="mercedes">Mercedes</option>
                <option value="audi">Audi</option>
            </select>

            <!--button, submit, reset should be not counted:-->
            <button id="button-no-value-with-text">Click me</button>
            <input type="submit" id="type-submit-with-value" value="Submit">
            <input type="reset" id="type-reset-with-value" value="Reset">

            <!--image and hidden should be not counted:-->
            <input type="image" id="type-image-with-src-no-value" src="{const.LOGO_PATH}">
            <input type="hidden" id="type-hidden-some-value" value="some">

            <!--range and color should be not counted
                because they always have at least 0 and #000000
                that can hardly be counted as "empty"-->
            <input type="range" id="type-range-0-value">
            <input type="color" id="type-color-000000-value">
        </form>

        <form id="form-with-text-with-values">
            <textarea id="textarea-with-value-with-text">textarea-with-value-with-text;</textarea>
            <input id="no-type-with-value" value="no-type-with-value;">
            <input id="no-type-explicit-empty-value" value="">

            <input type="text" id="type-text-with-value" value="type-text-with-value;">
            <input type="text" id="type-text-explicit-empty-value" value="">

            <input type="checkbox" id="type-checkbox-checked" name="vehicle1" value="Bike" checked>
            <label for="vehicle1"> I have a bike</label><br>

            <input type="radio" id="type-radio-checked" name="fav_language" value="HTML" checked>
            <label for="html">HTML</label><br>

            <select id="select-empty-value">
                <!--<option value=""></option>-->
                <option value="volvo">Volvo</option>
                <option value="saab">Saab</option>
                <option value="mercedes">Mercedes</option>
                <option value="audi">Audi</option>
            </select>

            <!--button, submit, reset should be not counted:-->
            <button id="button-no-value-with-text">Click me</button>
            <input type="submit" id="type-submit-with-value" value="Submit">
            <input type="reset" id="type-reset-with-value" value="Reset">

            <!--image and hidden should be not counted:-->
            <input type="image" id="type-image-with-src-no-value" src="{const.LOGO_PATH}">
            <input type="hidden" id="type-hidden-some-value" value="some">

            <!--range and color should be not counted
                because they always have at least 0 and #000000
                that can hardly be counted as "empty"-->
            <input type="range" id="type-range-0-value">
            <input type="color" id="type-color-000000-value">
        </form>
        '''
    )
    s('#form-no-text-with-values textarea').type('textarea-with-value-no-text;')

    # form element is considered empty if all "text-value" fields are empty
    s('#form-no-text-with-values').should(be.not_._empty)
    try:
        s('#form-no-text-with-values').should(be._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#form-no-text-with-values')).is empty\n"
            '\n'
            'Reason: ConditionMismatch: actual values of all form inputs, textareas and '
            'selects: '
            'textarea-with-value-no-text;no-type-with-value;type-text-with-value;BikeHTMLvolvo\n'
            'Screenshot: '
        ) in str(error)
    s('#form-with-text-with-values').should(be.not_._empty)
    try:
        s('#form-with-text-with-values').should(be._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#form-with-text-with-values')).is empty\n"
            '\n'
            'Reason: ConditionMismatch: actual values of all form inputs, textareas and selects: '
            'textarea-with-value-with-text;no-type-with-value;type-text-with-value;BikeHTMLvolvo\n'
        ) in str(error)
    s('#form-no-text-no-values').should(be._empty)
    try:
        s('#form-no-text-no-values').should(be.not_._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#form-no-text-no-values')).is not (empty)\n"
            '\n'
            'Reason: ConditionMismatch: actual values of all form inputs, textareas and '
            'selects: \n'  # todo: make empty string explicit via quotes (here and everywhere)
            'Screenshot: '
        ) in str(error)
    s('#form-with-text-no-values').should(be._empty)
    try:
        s('#form-with-text-no-values').should(be.not_._empty)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#form-with-text-no-values')).is not "
            '(empty)\n'
            '\n'
            'Reason: ConditionMismatch: actual values of all form inputs, textareas and '
            'selects: \n'
            'Screenshot: '
        ) in str(error)


def test_should_have_tabs_number__applied_to_browser__passed_and_failed(
    function_browser,
):
    browser = function_browser.with_(timeout=0.1, window_width=720, window_height=480)
    s = lambda selector: browser.element(selector)
    ss = lambda selector: browser.all(selector)
    GivenPage(browser).opened_empty()  # 1
    browser.driver.switch_to.new_window('tab')  # +1
    browser.driver.switch_to.new_window('window')  # +1
    browser.driver.switch_to.new_window('tab')  # +1
    # THEN
    # => expect 4 tabs total

    # have tabs_number?
    # todo: should we think on implementing somthing like:
    # browser.with_(_match_only_visible_window_tabs_number=True).should(
    #     match.tabs_number(2)
    # )

    browser.should(match.tabs_number(4))

    browser.should(have.no.tabs_number(5))
    browser.should(have.tabs_number(4))
    browser.should(have.no.tabs_number(3))

    try:
        browser.should(have.tabs_number(3))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            'browser.has tabs number 3\n'
            '\n'
            'Reason: ConditionMismatch: actual tabs number: 4\n'
            'Screenshot: '
            'file:'  # '///Users/yashaka/.selene/screenshots/1721056397813/1721056397813.png\n'
            # 'PageSource: '
            # 'file:///Users/yashaka/.selene/screenshots/1721056397813/1721056397813.html\n'
        ) in str(error)

    # WHEN
    browser.driver.switch_to.new_window('tab')  # +1
    browser.driver.close()  # -1

    # THEN
    # => still expect 4 tabs total

    browser.should(match.tabs_number(4))

    browser.should(have.no.tabs_number(5))
    browser.should(have.tabs_number(4))
    browser.should(have.no.tabs_number(3))

    try:
        browser.should(have.tabs_number(3))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            'browser.has tabs number 3\n'
            '\n'
            'Reason: ConditionMismatch: actual tabs number: 4\n'
            'Screenshot: cannot be saved because of: NoSuchWindowException: no such '
            'window: target window already closed\n'
            'from unknown error: web view not found\n'
            '  (Session info: chrome=126.0.6478.127)\n'
            'PageSource: cannot be saved because of: NoSuchWindowException: no such '
            'window: target window already closed\n'
            'from unknown error: web view not found\n'
            '  (Session info: chrome=126.0.6478.127)\n'
        ) in str(error)

    # have size or less?
    browser.should(have.tabs_number(5).or_less)
    browser.should(have.tabs_number(4).or_less)
    try:
        browser.should(have.tabs_number(3).or_less)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.has tabs number 3 or less\n"
            '\n'
            'Reason: ConditionMismatch: actual tabs number: 4\n'
        ) in str(error)
    browser.should(have.no.tabs_number(3).or_less)
    try:
        browser.should(have.no.tabs_number(4).or_less)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (  # TODO: fix it because now inversion does not come into action... in context of describing...
            "browser.has no (tabs number 4 or less)\n"
            '\n'
            'Reason: ConditionMismatch: actual tabs number: 4\n'
        ) in str(
            error
        )
    browser.should(have.no.tabs_number_less_than_or_equal(3))

    # todo: add a few failed cases below...

    # have size or more?
    browser.should(have.tabs_number(3).or_more)
    browser.should(have.tabs_number(4).or_more)
    browser.should(have.no.tabs_number(5).or_more)
    browser.should(have.no.tabs_number_greater_than_or_equal(5))

    # have size more than
    browser.should(have.no.tabs_number(4)._more_than)
    browser.should(have.no.tabs_number_greater_than(4))
    browser.should(have.tabs_number_greater_than(3))
    browser.should(have.tabs_number_greater_than(0))

    # have size less than
    browser.should(have.tabs_number_less_than(5))
    browser.should(have.no.tabs_number(4)._less_than)
    browser.should(have.no.tabs_number_less_than(4))
    browser.should(have.no.tabs_number_less_than(0))
