import pytest

from selene import be, have, query
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_browser_actions_drags_source_and_drops_it_to_target_with_implicit_waiting(
    session_browser,
):
    browser = session_browser.with_(
        timeout=3,  # GIVEN
    )
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
        timeout=0.5,  # GIVEN
    )

    # WHEN
    browser._actions.drag_and_drop(
        browser.element('#draggable'), browser.element('#target2')
    ).perform()

    browser.element('#target1').element('#draggable').should(be.not_.present)
    browser.element('#target2').element('#draggable').should(be.present)

    # WHEN
    browser._actions.click_and_hold(browser.element('#draggable')).release(
        browser.element('#target1')
    ).perform()

    browser.element('#target1').element('#draggable').should(be.present)
    browser.element('#target2').element('#draggable').should(be.not_.present)


def test_browser_actions_fails_to_wait_for_drag_and_drop_before_perform(
    session_browser,
):
    browser = session_browser.with_(
        timeout=0.5,  # GIVEN
    )
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
        timeout=1.0,  # GIVEN
    )

    # WHEN
    try:
        browser._actions.drag_and_drop(
            browser.element('#draggable'), browser.element('#target2')
        ).perform()
        pytest.fail('should fail with timeout')

    # THEN
    except TimeoutException as error:
        assert (
            "browser.element(('css selector', '#draggable')).locate webelement\n"
            "\n"
            "Reason: NoSuchElementException: "
            "no such element: Unable to locate element: "
            "{\"method\":\"css selector\",\"selector\":\"#draggable\"}\n"
        ) in str(error)
        # TODO: should we see in error something more like:
        # actions.drag_and_drop( browser.element('#draggable'), browser.element('#target2') )


# TODO: add test that simulate failure inside perform,
#       not inside actions registration in context of waiting for located webelement
