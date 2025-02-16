from selene.core._elements import All
from ._element import Element
from ._client import Browser


class Collection(
    All[Element],
):
    def __init__(self, locator, config, _Element=Element, **kwargs):
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            **kwargs,
        )
