import pytest

from typing import Optional

import selene
from selene.core.exceptions import TimeoutException
from selene import command, be, have, query
from tests.integration.helpers.givenpage import GivenPage


def test_js_drags_source_and_drops_it_to_target(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.add_style_to_head("""
        #target1, #target2 {
          float: left;
          width: 100px;
          height: 35px;
          margin: 10px;
          padding: 10px;
          border: 1px solid black;
        }
    """)
    page.add_script_to_head("""
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
    """)
    page.load_body("""
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
    """)

    # WHEN
    browser.element('#draggable').perform(
        command.js.drag_and_drop_to(browser.element('#target2'))
    )

    browser.element('#target1').element('#draggable').should(be.not_.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.present_in_dom)

    # WHEN
    browser.element('#draggable').with_(drag_and_drop_by_js=True).drag_and_drop_to(
        browser.element('#target1')
    )

    browser.element('#target1').element('#draggable').should(be.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.not_.present_in_dom)


class ReactContinuousSlider:
    def __init__(self, browser: Optional[selene.Browser]):
        self.browser = browser if browser else selene.browser
        self.container = self.browser.element('#ContinuousSlider+*')
        self.thumb = self.container.element('.MuiSlider-thumb')
        self.thumb_input = self.thumb.element('input')
        self.volume_up = self.container.all('svg').second
        self.volume_down = self.container.all('svg').first
        # self.volume_up = self.container.element('[data-testid=VolumeUpIcon]')
        # self.volume_down = self.container.element('[data-testid=VolumeDownIcon]')
        self.rail = self.container.element('.MuiSlider-rail')

    def open(self):
        self.browser.open('https://mui.com/material-ui/react-slider/#ContinuousSlider')
        return self


def test_js_does_not_drag_react_mui_slider(session_browser):
    browser = session_browser.with_(timeout=1.0)
    slider = ReactContinuousSlider(browser).open()
    original_value = slider.thumb_input.get(query.value)

    slider.thumb.perform(command.js.drag_and_drop_to(slider.volume_up))

    slider.thumb_input.should(have.value(original_value))
    slider.thumb_input.should(have.no.value('100'))


def test_js_drag_and_drop_to_asserts_location_changed_when_requested(session_browser):
    browser = session_browser
    page = GivenPage(browser.driver)
    page.opened_with_body("""
        <style>
            #source {
                position: absolute;
                left: 10px;
                top: 10px;
                width: 50px;
                height: 50px;
                background: red;
            }

            #target {
                position: absolute;
                left: 200px;
                top: 10px;
                width: 50px;
                height: 50px;
                background: blue;
            }
        </style>

        <div id="source" draggable="true"></div>
        <div id="target"></div>

        <script>
            const source = document.querySelector('#source')
            const target = document.querySelector('#target')

            source.addEventListener('dragstart', event => {
                event.dataTransfer.setData('text/plain', 'source')
            })

            target.addEventListener('drop', event => {
                event.preventDefault()
                // intentionally do nothing:
                // source location should remain unchanged
            })
        </script>
    """)

    browser.config.timeout = 0.1

    with pytest.raises(TimeoutException):
        browser.element('#source').perform(
            command.js.drag_and_drop_to(
                browser.element('#target'),
                _assert_location_changed=True,
            )
        )


def test_element_drag_and_drop_to_by_js_asserts_location_changed_when_requested(
    session_browser,
):
    browser = session_browser
    page = GivenPage(browser.driver)
    page.opened_with_body("""
        <style>
            #source {
                position: absolute;
                left: 10px;
                top: 10px;
                width: 50px;
                height: 50px;
                background: red;
            }

            #target {
                position: absolute;
                left: 200px;
                top: 10px;
                width: 50px;
                height: 50px;
                background: blue;
            }
        </style>

        <div id="source" draggable="true"></div>
        <div id="target"></div>

        <script>
            const source = document.querySelector('#source')
            const target = document.querySelector('#target')

            source.addEventListener('dragstart', event => {
                event.dataTransfer.setData('text/plain', 'source')
            })

            target.addEventListener('drop', event => {
                event.preventDefault()
                // intentionally do nothing
            })
        </script>
    """)

    browser.config.timeout = 0.1

    with pytest.raises(TimeoutException):
        browser.element('#source').with_(drag_and_drop_by_js=True).drag_and_drop_to(
            browser.element('#target'),
            _assert_location_changed=True,
        )
