# How to simplify search by Test IDs in Selene?

{% include-markdown 'warn-from-next-release.md' %}

– By customizing [config.selector_to_by_strategy][selene.core.configuration.Config.selector_to_by_strategy] as simply as:

```python
# tests/conftest.py
import re
import pytest
import selene
from selene.common.helpers import _HTML_TAGS


@pytest.fixture(scope="function", autouse=True)
def browser_management():
    selene.browser.config.selector_to_by_strategy = lambda selector: (
        # wrap into default strategy (to not redefine from scratch auto-xpath-detection)
        selene.browser.config.selector_to_by_strategy(
            # detected testid
            f"[data-testid={selector}]"  # ⬅️
            if re.match(
                # word_with_dashes_underscores_or_numbers
                r"^[a-zA-Z_\d\-]+$",
                selector,
            )
            and selector not in _HTML_TAGS
            else selector
        )
    )

    yield

    selene.browser.quit()
```

You can adapt this code to the specific name of you test id attribute, e.g. `data-test-id`, `data-test`, `data-qa`, `test-id`, `testid`, etc.

Thus, you can use:

```python
# tests/test_duckduckgo.py
from selene import browser, by, have


def test_search():
    browser.open('https://www.duckduckgo.org/')
    browser.element('[name=q]').type('github yashaka selene python').press_enter()

    browser.all('result').first.element('result-title-a').click()  # 💡😇

    browser.should(have.title_containing('yashaka/selene'))
```

over:

```python
# tests/test_duckduckgo.py
from selene import browser, by, have


def test_search():
    browser.open('https://www.duckduckgo.org/')
    browser.element('[name=q]').type('github yashaka selene python').press_enter()

    browser.all('[data-testid=result]').first.element(  # 🙈
        '[data-testid=result-title-a]'  # 🙈
    ).click()

    browser.should(have.title_containing('yashaka/selene'))
```

See a bigger example of utilizing same technique with [Page Object Model pattern applied to the DataGrid React component](https://github.com/yashaka/selene/blob/master/tests/examples/pom/test_material_ui__react_x_data_grid__mit.py).
