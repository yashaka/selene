import pytest

from selene import be, have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_drag_and_drop_moves_element_between_targets(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=3)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.add_style_to_head(
        """
        #target1, #target2 {
          float: left;
          width: 100px;
          height: 35px;
          margin: 10px;
          padding: 10px;
          border: 1px solid black;
        }
        """
    )
    page.add_script_to_head(
        """
        function allowDrop(ev) {
          ev.preventDefault();
        }

        function drag(ev) {
          ev.dataTransfer.setData('text', ev.target.id);
        }

        function drop(ev) {
          ev.preventDefault();
          var data = ev.dataTransfer.getData('text');
          ev.target.appendChild(document.getElementById(data));
        }
        """
    )
    page.load_body_with_timeout(
        '''
        <h2>Drag and Drop</h2>
        <p>Drag the image back and forth between the two div elements.</p>

        <div id="target1" ondrop="drop(event)" ondragover="allowDrop(event)">
          <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
               id="draggable"
               draggable="true"
               ondragstart="drag(event)"
               width="40"
               height="40"
          >
        </div>

        <div id="target2" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
        ''',
        timeout=0.5,
    )

    # WHEN
    browser._actions.drag_and_drop(
        browser.element('#draggable'), browser.element('#target2')
    ).perform()

    # THEN
    browser.element('#target1').element('#draggable').should(be.not_.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.present_in_dom)

    # WHEN
    browser._actions.click_and_hold(browser.element('#draggable')).release(
        browser.element('#target1')
    ).perform()

    # THEN
    browser.element('#target1').element('#draggable').should(be.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.not_.present_in_dom)


def test_drag_and_drop_fails_with_timeout(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.add_style_to_head(
        """
        #target1, #target2 {
          float: left;
          width: 100px;
          height: 35px;
          margin: 10px;
          padding: 10px;
          border: 1px solid black;
        }
        """
    )
    page.add_script_to_head(
        """
        function allowDrop(ev) {
          ev.preventDefault();
        }

        function drag(ev) {
          ev.dataTransfer.setData('text', ev.target.id);
        }

        function drop(ev) {
          ev.preventDefault();
          var data = ev.dataTransfer.getData('text');
          ev.target.appendChild(document.getElementById(data));
        }
        """
    )
    page.load_body_with_timeout(
        '''
        <h2>Drag and Drop</h2>
        <p>Drag the image back and forth between the two div elements.</p>

        <div id="target1" ondrop="drop(event)" ondragover="allowDrop(event)">
          <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
               id="draggable"
               draggable="true"
               ondragstart="drag(event)"
               width="40"
               height="40"
          >
        </div>

        <div id="target2" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
        ''',
        timeout=1.0,
    )

    # WHEN / THEN
    with pytest.raises(TimeoutException) as error:
        browser._actions.drag_and_drop(
            browser.element('#draggable'), browser.element('#target2')
        ).perform()

    assert (
        "browser.element(('css selector', '#draggable')).locate webelement"
        in str(error.value)
    )
