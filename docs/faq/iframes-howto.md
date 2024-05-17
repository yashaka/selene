# How to work with iframes in Selene?

You allways can work with iframes same way [as you do in pure Selenium](https://www.selenium.dev/documentation/webdriver/interactions/frames), by using `browser.driver.switch_to.*` commands:

```python
from selene import browser, command, have



# GIVEN
iframe = browser.element('#editor-iframe')
# WHEN
iframe_webelement = iframe.locate()
# THEN
browser.driver.switch_to.frame(iframe_webelement)
# AND work with textarea inside frame:
browser.element('.textarea').type('Hello, World!').perform(command.select_all)
# AND switch back...
browser.driver.switch_to.default_content()
# AND deal with elements outside iframe
browser.element('#toolbar').element('#bold').click()
# AND come back to ...
browser.driver.switch_to.frame(iframe_webelement)
# AND ...
browser.element('.textarea').should(
    have.js_property('innerHTML').value(
        '<p><strong>Hello, world!</strong></p>'
    )
)
```

In addition to that, Selene provides an experimental feature – [`query._frame_context`][selene.core.query._frame_context], that removes a bit of boilerplate:

=== "with frame context"

    ```python
    from selene import browser, command, have, query


    ...
    # GIVEN
    iframe = browser.element('#editor-iframe')
    # WHEN

    # THEN
    with iframe.get(query._frame_context):
        # AND work with textarea inside frame:
        browser.element('.textarea').type('Hello, World!').perform(command.select_all)
        # AND switch back AUTOMATICALLY...

    # AND deal with elements outside iframe
    browser.element('#toolbar').element('#bold').click()
    # AND come back to ...
    with iframe.get(query._frame_context):
        # AND ...
        browser.element('.textarea').should(
            have.js_property('innerHTML').value(
                '<p><strong>Hello, world!</strong></p>'
            )
        )
    ```

=== "with frame context (comments removed, formatted)"

    ```python
    from selene import browser, command, have, query


    ...

    iframe = browser.element('#editor-iframe')



    with iframe.get(query._frame_context):

        browser.element('.textarea').type('Hello, World!').perform(command.select_all)



    browser.element('#toolbar').element('#bold').click()

    with iframe.get(query._frame_context):

        browser.element('.textarea').should(
            have.js_property('innerHTML').value(
                '<p><strong>Hello, world!</strong></p>'
            )
        )
    ```

=== "driver.switch_to.*"

    ```python
    from selene import browser, command, have




    iframe = browser.element('#editor-iframe')

    iframe_webelement = iframe.locate()

    browser.driver.switch_to.frame(iframe_webelement)

    browser.element('.textarea').type('Hello, World!').perform(command.select_all)

    browser.driver.switch_to.default_content()

    browser.element('#toolbar').element('#bold').click()

    browser.driver.switch_to.frame(iframe_webelement)

    browser.element('.textarea').should(
        have.js_property('innerHTML').value(
            '<p><strong>Hello, world!</strong></p>'
        )
    )
    ```

!!! note

    Some examples above and below are formatted and aligned for easier comparison of the corresponding parts of code. The additional new lines are added so you can directly see the differences between the examples.

It also has a handy [`_within`][selene.core.query._frame_context._within] decorator to tune PageObject steps to work with iframes:

=== "_within decorator"

    ```python
    from selene import browser, command, have, query


    class Editor:

        area_frame = browser.element('#editor-iframe').get(query._frame_context)
        text_area = browser.element('.textarea')
        toolbar = browser.element('#toolbar')

        @area_frame._within
        def type(self, text):
            self.text_area.type(text)
            return self

        @area_frame._within
        def select_all(self):
            self.text_area.perform(command.select_all)
            return self

        def set_bold(self):
            self.toolbar.element('#bold').click()
            return self

        @area_frame._within
        def should_have_content_html(self, text):
            self.text_area.should(
                have.js_property('innerHTML').value(
                    text
                )
            )
            return self
    ```

=== "+ using PageObject"

    ```python
    from selene import browser, command, have, query
    from my_project.pages import Editor

    ...

    editor = Editor()

    editor.type('Hello, World!').select_all().set_bold()

    editor.should_have_content_html(
        '<p><strong>Hello, world!</strong></p>'
    )
    ```

=== "using PageObject (formatted)"

    ```python
    from selene import browser, command, have, query
    from my_project.pages import Editor

    ...

    editor = Editor()





    editor.type('Hello, World!').select_all().set_bold()






    editor.should_have_content_html(

        '<p><strong>Hello, world!</strong></p>'

    )
    ```

=== "with operator"

    ```python
    from selene import browser, command, have, query


    ...

    iframe = browser.element('#editor-iframe')



    with iframe.get(query._frame_context):

        browser.element('.textarea').type('Hello, World!').perform(command.select_all)


    browser.element('#toolbar').element('#bold').click()

    with iframe.get(query._frame_context):

        browser.element('.textarea').should(
            have.js_property('innerHTML').value(
                '<p><strong>Hello, world!</strong></p>'
            )
        )
    ```

See a more detailed explanation and examples on [the feature reference][selene.core.query._frame_context].
