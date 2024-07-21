from typing import Optional

import selene
from selene import command, be, have, query
from selene.support._pom import Element
from tests.integration.helpers.givenpage import GivenPage


def test_drags_source_and_drops_it_to_target(session_browser):
    browser = session_browser.with_(timeout=2)
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
    page.load_body(
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
        '''
    )

    # WHEN
    browser.element('#draggable').perform(
        command.drag_and_drop_to(browser.element('#target2'))
    )

    browser.element('#target1').element('#draggable').should(be.not_.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.present_in_dom)

    # WHEN
    browser.element('#draggable').perform(
        command.drag_and_drop_to(browser.element('#target1'))
    )

    browser.element('#target1').element('#draggable').should(be.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.not_.present_in_dom)


def test_drags_source_and_drops_it_to_target_with_forced_retry(session_browser):
    browser = session_browser.with_(timeout=2)
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
        var counter = 0;

        function allowDrop(ev) {
          ev.preventDefault();
        }

        function drag(ev) {
          ev.dataTransfer.setData('text', ev.target.id);
        }

        function drop(ev) {
          if (counter < 3) { // <-- GIVEN
            counter++;
            return;
          }
          ev.preventDefault();
          var data = ev.dataTransfer.getData('text');
          ev.target.appendChild(document.getElementById(data));
        }
        """
    )
    page.load_body(
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
        '''
    )

    # WHEN
    browser.element('#draggable').perform(
        command.drag_and_drop_to(browser.element('#target2'))
    )

    browser.element('#target1').element('#draggable').should(be.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.not_.present_in_dom)

    # WHEN
    browser.element('#draggable').perform(
        command.drag_and_drop_to(
            browser.element('#target2'), _assert_location_changed=True
        )
    )

    browser.element('#target1').element('#draggable').should(be.not_.present_in_dom)
    browser.element('#target2').element('#draggable').should(be.present_in_dom)


# Example of the classic OOP-like PageObject pattern
class __X_ReactContinuousSlider:
    def __init__(self, browser: Optional[selene.Browser]):
        self.browser = browser if browser else selene.browser
        self.context = self.browser.element('#ContinuousSlider+*')

        self.thumb = self.context.element('.MuiSlider-thumb')
        self.thumb_input = self.thumb.element('input')
        self.volume_up = self.context.element('[data-testid=VolumeUpIcon]')
        self.volume_down = self.context.element('[data-testid=VolumeDownIcon]')
        self.rail = self.context.element('.MuiSlider-rail')

    def open(self):
        self.browser.open('https://mui.com/material-ui/react-slider/#ContinuousSlider')
        return self


# Example of the POM-like PageObject pattern
class ReactContinuousSlider:
    thumb = Element('.MuiSlider-thumb')
    thumb_input = thumb.Element('input')
    volume_up = Element('[data-testid=VolumeUpIcon]')
    volume_down = Element('[data-testid=VolumeDownIcon]')
    rail = Element('.MuiSlider-rail')

    def __init__(self, browser: Optional[selene.Browser]):
        self.browser = browser or selene.browser
        self.context = self.browser.element('#ContinuousSlider+*')

    def open(self):
        self.browser.open('https://mui.com/material-ui/react-slider/#ContinuousSlider')
        return self


def test_drags_react_mui_slider(session_browser):
    browser = session_browser.with_(timeout=1.0)
    slider = ReactContinuousSlider(browser).open()

    # WHEN
    slider.thumb.perform(command.drag_and_drop_to(slider.volume_up))

    slider.thumb_input.should(have.value('100'))

    # WHEN
    slider.thumb.perform(command.drag_and_drop_to(slider.rail))

    slider.thumb_input.should(have.value('50'))

    # WHEN
    slider.thumb.perform(command.drag_and_drop_to(slider.volume_down))

    slider.thumb_input.should(have.value('0'))
