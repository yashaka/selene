from selene import command, Element
from selene.core.wait import Command
import inspect


def test_command_js_click__is_a_command_on_element_instance():

    assert Command in inspect.getmro(command.js.click.__class__)
    # TODO: what else can we check? How can we check that it is Command[Element]?
