# How Selene compares to other frameworks

<!-- markdownlint-disable MD046 -->

!!! note "About this page"

    Written by the Selene maintainers, so expect a natural bias — that's why every claim
    about other frameworks is sourced to their official documentation, and Selene's own
    limitations get their own section below.

    All maintenance data (versions, release dates, stars) was collected from official
    registries (PyPI, npm, Maven Central via GitHub releases) and the GitHub API on
    **2026-11-08**. Stars are live counters and drift by ±1 between checks.

## Project health at a glance

| Framework | Latest release | Stars | Maintainer | Status |
|---|---|---|---|---|
| Selenium | 4.52.0 (2026-10-29) | — | Software Freedom Conservancy / community | Active, W3C standard |
| SeleniumBase | 4.57.1 (2026-11-05) | ~13.2k | Solo + community | Active |
| Splinter | 0.21.0 (2024-01-16) | ~2.7k | Community | Semi-maintained (no release since 01.2024) |
| Helium | 7.0.4 (2026-10-22) | ~8.3k | Solo | Active |
| Pylenium | 1.21.0 (2024-05-24) | ~0.3k | Solo | Unmaintained (no commits since 05.2024) |
| Selenide | 7.19.1 (2026-10-25) | ~1.9k | Community | Active |
| Cypress | 16.2.1 (2026-10-28) | ~51k | Company (Cypress.io) + paid cloud | Active |
| Playwright | 1.64.1 (2026-10-22) | ~15.1k | Microsoft | Active |
| **Selene** | 2.0.0rc10 (2026-05-20, rc11 in development) | ~0.7k | Solo | 2.0 in release-candidate stage |

## What we compare

The same axes are applied to every framework:

1. **Locator model** — are returned elements re-resolved on each use (lazy), or do they
   go stale?
2. **Waiting model** — what waits automatically, and where do you still hand-write waits?
3. **Assertions** — do built-in assertions retry until the condition is met?
4. **Conditions composability** — can you write your own reusable wait-conditions as a
   first-class API?
5. **Collections** — do collection queries wait, or return instant snapshots?
6. **Debug artifacts** — what do you get on failure without extra setup?
7. **Runner & parallelism** — what do you run tests with?
8. **Architecture** — WebDriver protocol vs own driver.
9. **Browsers** — including the branded Safari.

## The same test in every framework

Scenario: open `https://google.com/ncr`, type `selenium` into the search box, press
`Enter`, then check that there are more than 5 results and the first one mentions
*Selenium automates browsers*.

=== "Selenium"

    ```python
    # pip install selenium==4.52.0
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = webdriver.Chrome()  # chromedriver managed by Selenium Manager (since 4.6)
    wait = WebDriverWait(driver, 10)

    driver.get('https://google.com/ncr')

    search = driver.find_element(By.NAME, 'q')
    search.send_keys('selenium')
    search.send_keys(Keys.ENTER)

    wait.until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, '#rso>div'), 'Selenium automates browsers'))

    results = driver.find_elements(By.CSS_SELECTOR, '#rso>div')
    assert len(results) > 5
    assert 'Selenium automates browsers' in results[0].text
    ```

=== "Splinter"

    ```python
    # pip install splinter==0.21.0
    from splinter import Browser

    browser = Browser('chrome')  # a selenium driver under the hood

    browser.visit('https://google.com/ncr')

    browser.find_by_name('q').fill('selenium')
    browser.find_by_name('btnK').click()

    assert browser.is_text_present('Selenium automates browsers')  # polls up to 2s
    assert len(browser.find_by_css('#rso>div')) > 5
    ```

=== "Helium"

    ```python
    # pip install helium==7.0.4
    from helium import start_chrome, write, press, ENTER, S, Text, wait_until, find_all

    start_chrome('https://google.com/ncr')

    write('selenium', into=S('input[name=q]'))
    press(ENTER)

    wait_until(Text('Selenium automates browsers').exists)  # waits up to 10s
    assert len(find_all(S('#rso>div'))) > 5
    ```

=== "SeleniumBase"

    ```python
    # pip install seleniumbase==4.57.1
    from seleniumbase import BaseCase

    class TestGoogleSearch(BaseCase):
        def test_finds_selenium(self):
            self.open('https://google.com/ncr')
            self.type('input[name=q]', 'selenium\n')  # waits visible+interactive, "\n" submits
            self.assert_element('#rso>div:nth-of-type(5)')  # the 5th result exists
            self.assert_text('Selenium automates browsers', '#rso>div')
    ```

=== "Pylenium (unmaintained)"

    ```python
    # pip install pyleniumio==1.21.0  # last release 2024-05-24, not maintained since
    def test_finds_selenium(py):
        py.visit('https://google.com/ncr')
        py.get('input[name=q]').type('selenium\n')
        py.contains('Selenium automates browsers').should().be_visible()
    ```

=== "Selenide (Java)"

    ```java
    // testImplementation "com.codeborne:selenide:7.19.1"
    import org.junit.jupiter.api.Test;
    import static com.codeborne.selenide.Selenide.*;
    import static com.codeborne.selenide.Condition.text;
    import static com.codeborne.selenide.CollectionCondition.sizeGreaterThan;

    class GoogleSearchTest {
        @Test
        void findsSelenium() {
            open("https://google.com/ncr");
            $("[name=q]").setValue("selenium").pressEnter();
            $$("#rso>div").shouldHave(sizeGreaterThan(5));
            $$("#rso>div").first().shouldHave(text("Selenium automates browsers"));
        }
    }
    ```

=== "Cypress (JS)"

    ```javascript
    // npm install cypress@16.2.1
    describe('google search', () => {
      it('finds Selenium', () => {
        cy.visit('https://google.com/ncr')
        cy.get('input[name=q]').type('selenium{enter}')
        cy.get('#rso>div').should('have.length.greaterThan', 5)
        cy.get('#rso>div').first().should('contain.text', 'Selenium automates browsers')
      })
    })
    ```

=== "Playwright (Python)"

    ```python
    # pip install playwright==1.64.1 pytest-playwright==0.10.0 && playwright install
    from playwright.sync_api import Page, expect


    def test_finds_selenium(page: Page):
        page.goto('https://google.com/ncr')

        query = page.locator('input[name=q]')
        query.fill('selenium')
        query.press('Enter')

        results = page.locator('#rso>div')
        expect(results.nth(4)).to_be_visible()  # >5 results: the 5th is visible
        expect(results.first).to_contain_text('Selenium automates browsers')
    ```

=== "Selene"

    ```python
    # pip install selene==2.0.0rc10
    from selene import browser, by, be, have

    browser.open('https://google.com/ncr')

    browser.element(by.name('q')).should(be.blank) \
        .type('selenium').press_enter()

    browser.all('#rso>div').should(have.size_greater_than(5)) \
        .first.should(have.text('Selenium automates browsers'))
    ```

Read the examples top to bottom and the philosophy differences become visible: in raw
Selenium you manage waiting explicitly, in most wrappers you get partial automatic
waiting, and in Selenide-style libraries (Selenide, Selene) and Playwright/Cypress every
line both locates and waits.

<!-- markdownlint-enable MD046 -->

## Framework by framework

### Selenium WebDriver — the baseline

Everything else on this page is either built on top of Selenium or competes with it.
"WebDriver drives a browser natively, as a user would, either locally or on a remote
machine using the Selenium server." It is a [W3C Recommendation][selenium-webdriver].

- Driver and browser setup is solved out of the box: [Selenium Manager][selenium-manager]
  "provides automated driver and browser management for Selenium. Selenium bindings use
  this tool by default" (drivers since 4.6; automatic browser downloads for Chrome
  since 4.11, Firefox since 4.12, Edge since 4.14).
- No automatic waiting: the implicit wait "default value is 0, which means that if the
  element is not found, it will immediately return an error". Explicit waits are
  "loops added to the code that poll the application for a specific condition" —
  and the docs warn: "Do not mix implicit and explicit waits. Doing so can cause
  unpredictable wait times." [selenium-waits]
- Stale elements are the user's problem: `stalenessOf` is documented as "An element is
  no longer attached to the DOM" — you re-find and re-wait yourself. [selenium-waits]
- WebDriver BiDi is coming up as "the cross-browser replacement for the Chrome DevTools
  Protocol" — network, logging and script events over WebSocket. [selenium-webdriver]
- Browsers: Chrome, Edge, Firefox, Safari (via safaridriver), IE legacy.
  [selenium-browsers]
- The ecosystem is unmatched: Selenium Grid, every cloud provider, every language.

**Non-obvious:** everything above is also its weakness — zero auto-wait by default,
no screenshots/reporting on failure out of the box, verbose boilerplate. Wrappers exist
for a reason.

### Splinter

"Splinter is a simple and consistent API for web application automation", "Easy to
learn: The API is designed to be intuitive and quick to pick up." [splinter-docs]

- Thin wrapper over the "Selenium, Django, Flask, ZopeTestBrowser" drivers. [splinter-docs]
- Waiting is opt-in polling: `is_text_present(text, wait_time=None)` "Number of seconds
  to search for the text" — the code default is `wait_time = wait_time or self.wait_time`
  with `wait_time=2` in the WebDriver driver constructor. [splinter-api] [splinter-src]
- `find_by_*` returns an `ElementList` that is an eager snapshot: the query runs at the
  call site (`find_by_css → self.find_by(self.driver.find_elements, ...)`), there is no
  re-resolution later. [splinter-src]
- Has screenshots support. [splinter-screenshots]

**Non-obvious downsides:** the last release is 0.21.0 from 2024-01-16 (repo still gets
occasional pushes, but no releases for almost 3 years); no automatic actionability
waiting like the Selenide-style frameworks; a thin API means thin batteries — reporting
and artifacts are on you.

### Helium

"Lighter web automation with Python" — "The name Helium was chosen because it is also a
chemical element like Selenium, but it is lighter." [helium-readme]

- Waiting: "Helium by default waits up to 10 seconds for the element to appear", plus an
  explicit `wait_until(Button('Download').exists)`. [helium-readme]
- Architecture: "Under the hood, Helium forwards each call to Selenium" and "you can
  freely mix the two libraries". [helium-readme]
- Killer features are DX-level: "Helium scripts are typically 30-50% shorter than similar
  Selenium scripts"; elements by user-visible labels instead of selectors; interacting
  with iFrames "without having to first 'switch to' the iFrame"; "Helium notices when
  popups open or close and focuses / defocuses them like a user would." [helium-readme]

**Non-obvious downsides:** a solo maintainer — the README itself says the Java
implementation was dropped because of lacking time; browser support is documented as
"automating browsers such as Chrome and Firefox" — Safari support is not documented;
the API surface is intentionally small, which is great for scripts and limiting for
large Page Object suites; element re-resolution behavior is not documented.

### SeleniumBase

"SeleniumBase is a Python framework for browser automation and testing. SeleniumBase
uses Selenium/WebDriver APIs and incorporates test-runners such as pytest, pynose, and
behave." [seleniumbase-readme]

- Automatic waiting on actions: "✅ No More Flaky Tests! SeleniumBase methods
  automatically wait for page elements to finish loading before interacting with them
  (up to a timeout limit)." A single `self.type(selector, text)` "1. Waits for the
  element to be visible. 2. Waits for the element to be interactive. 3. Clears the text
  field. 4. Types in the new text. 5. Presses Enter/Submit if the text ends in "\n"."
  `sb.assert_*` methods "wait up to 7 seconds for the expected condition".
  [seleniumbase-readme]
- Batteries: a built-in [Recorder][seleniumbase-recorder] / test generator, a
  `--dashboard` HTML dashboard, reports, screenshots of failing tests saved to
  `./latest_logs/` — "Raw Selenium does not have these options out-of-the-box". UC Mode
  / CDP Mode for bot-detection-heavy sites. [seleniumbase-readme]
- Parallelism: `pytest-xdist==3.8.0` ships as a pinned dependency, and Selenium Grid is
  documented for distributing tests. [seleniumbase-deps] [seleniumbase-readme]

**Non-obvious downsides:** the feature surface is huge and "magical" — methods call
JavaScript under the hood ("make sure that the readyState of the page is complete
before advancing", skippable via `--sjw`), some methods can dismiss pop-ups as a side
effect; there are several API layers (BaseCase methods, `sb.*`, pytest fixtures, raw
Selenium) and choosing between them is on you; assertions wait up to 7 seconds by
default — implicit behavior you should know about.

### Pylenium — unmaintained

"Bring the best of Selenium, Cypress and Python into one package." Pylenium "looks to
bring more Cypress-like bindings and techniques to Selenium (like automatic waits)".
[pylenium-readme]

We include it for completeness because people still find it in searches — but the last
release and the last commit are both from **2024-05-24**. Building anything new on it
in 2026 means owning its maintenance yourself. If you liked the idea (Cypress-like API
on top of Selenium), Selene is the maintained framework in that niche.

### Selenide (Java) — Selene's parent

"Selenide: concise UI tests in Java", "Selenide is a framework for test automation
powered by Selenium WebDriver". It defines a "concise fluent API, natural language
assertions and does some magic for ajax-based applications". [selenide-site]
[selenide-readme]

- "Yes, Selenide takes screenshots automatically on every test failure" — and
  `Selenide.screenshot("name")` saves both `.png` and `.html` (page source).
  [selenide-screenshots]
- Lazily re-resolved `$`/`$$` elements, fluent `should/be/have` conditions, collection
  conditions like `sizeGreaterThan`. [selenide-site]
- Selene is a direct port of these ideas: the Selene README states "Selene -
  User-oriented Web UI browser tests in Python (Selenide port)" and "Selene was inspired
  by Selenide from Java world." [selene-readme]

**Non-obvious:** if your team is on the JVM, Selenide is the most battle-tested
incarnation of this philosophy — 7.19.1 released 2026-10-25, actively maintained.

### Cypress (JS/TS)

A platform positioned as "a quality platform for teams shipping modern web
applications". The architecture claim is explicit: "Our architecture doesn't use
Selenium or WebDriver." — "Cypress is executed in the same run loop as your
application." [cypress-why]

- Retry-ability: "Queries link up, retrying the entire chain together. Assertions are a
  type of query... Non-queries only execute once." Default command timeout: 4 seconds
  (`defaultCommandTimeout`). [cypress-retry]
- Actions wait for actionability — "Action commands - such as .click() - automatically
  wait until multiple built-in assertions like these pass, and then it will attempt the
  action once" — but the action itself is not retried: "Cypress will not retry the
  .click() action command". [cypress-retry]
- Best-in-class debugging: Time Travel snapshots, videos, readable errors, Test Replay
  (in the paid Cloud). [cypress-why]
- Cross-browser: "Chrome-family browsers, Firefox, and WebKit (Safari's browser
  engine)". The branded Safari is not on the list. [cypress-cross]

**Non-obvious downsides — documented by Cypress itself** in the permanent trade-offs:
"Cypress is not a general purpose automation tool."; "You cannot use Cypress to drive
two browsers at the same time."; "Each test is bound to a single superdomain."
(cross-origin needs `cy.origin`); "The only language we'll ever support is the language
of the web: JavaScript."; there is no native `cy.hover()`; iframes support is "somewhat
limited". [cypress-tradeoffs] Mid-chain assertions act as retry boundaries — the docs
themselves describe the resulting "subject is no longer attached to the DOM" failure
mode. [cypress-retry] Parallelization and analytics live in the paid Cypress Cloud.
[cypress-why] And it is a JS/TS tool — if your stack is Python, Cypress competes for
your E2E budget, not for your test code.

### Playwright (Python)

"Playwright enables reliable web automation for testing, scripting, and AI agents." The
headline promise: "Playwright waits for elements to be actionable before performing
actions. Assertions automatically retry until conditions are met. No artificial
timeouts, no flaky tests." [playwright-home]

- Locators are lazy: "Every time a locator is used for an action, an up-to-date DOM
  element is located in the page." [playwright-locators]
- Strict mode is on by default: operations on locators "will throw an exception if more
  than one element matches" — opt-out is per-locator via `.first`/`.last`/`.nth()`.
  [playwright-locators]
- 28 auto-retrying `expect(locator).to_*` assertions (default timeout 5 seconds), soft
  assertions (pytest plugin ≥ 0.8.0), `expect.set_options(timeout=...)` globally.
  [playwright-assertions]
- Toolchain: Trace Viewer (DOM snapshots, network, console), codegen, Inspector
  (`PWDEBUG=1`), video recording, HAR record/replay, network mocking via `page.route()`.
  [playwright-trace] [playwright-mock]
- Parallelism via `pytest-xdist`; there is no own test runner in Python —
  "Playwright provides a Pytest plugin to write end-to-end tests." [playwright-runners]

**Non-obvious downsides:** instant reads don't wait — "locator.all() does not wait for
elements to match the locator, and instead immediately returns whatever is present in
the page... will produce unpredictable and flaky results"; `count()` and
`all_text_contents()` are instant too, and the docs tell you to prefer
`expect(locator).to_have_count()` instead. [playwright-locator-api] There is no API to
write your own web-first matchers in Python (`expect.extend` and `expect.poll` exist
only in the Node version) — custom assertions become hand-rolled wrappers.
[playwright-assertions] [playwright-assertions-node] The bundled Firefox and WebKit are
patched builds: "Playwright doesn't work with the branded version of Safari since it
relies on patches." [playwright-browsers] Each Playwright version needs its own browser
binaries; Selenium Grid integration is "experimental", Chrome/Edge only.
[playwright-grid] UI Mode exists only in the Node version of Playwright Test.

### Selene 2.0

"Selene - User-oriented Web UI browser tests in Python (Selenide port)" — "Selene was
inspired by Selenide from Java world." [selene-readme]

**Killer features** (all verifiable in the Selene 2.0 source, `selene/core/`):

- *Tests as prose, zero explicit waits.* Every action and every assertion is backed by
  one waiting engine (`class Wait` in `wait.py`) — you don't choose between "act" and
  "assert then wait": `browser.element('#login').should(have.text('Hi'))` reads the same
  way an action line does.
- *Lazy entities you can store.* Elements and collections are re-resolved on each use —
  you store **elements**, not locators, and they don't go stale:

  ```python
  menu_items = browser.all('.menu li')  # nothing is searched yet
  menu_items.first.should(have.text('Home'))  # search happens (and re-happens) here
  ```

- *Conditions as a first-class API.* 30 ready-made condition factories for elements,
  collections and the browser (`element_has_text`, `collection_has_size`,
  `browser_has_url`, ...) in `match.py`, exposed as `have.*`/`be.*` — and custom
  conditions are built with the same `Condition` class, so your domain-specific waits
  become reusable vocabulary. This is the axis where Playwright-Python has no
  equivalent API (see its section above).
- *Query API for reads and artifacts:* `element.get(query.attribute('href'))`,
  `query.screenshot_saved`, `query.page_source_saved` — reads are explicit, artifacts
  are queries too.
- *Sensible failure artifacts by default:* `save_screenshot_on_failure: bool = True`
  (plus page source and logged HTML of the failed element via config). [selene-config]
- *Selenide inheritance* — the mental model is the same if you come from the JVM.
  [selene-readme]

**Honest limitations:**

- *Bus factor and community size:* ~0.7k stars, a solo active maintainer, 113 open
  issues. SeleniumBase has ~18x the stars; Playwright is backed by Microsoft. Selene
  survives because its core is small — but it is a fact to weigh.
- *2.0 has been in release-candidate stage for over two years* — rc9 was published
  2024-03-06, rc10 followed only on 2026-05-20, rc11 is in development. The API is
  stable in practice, but the release rhythm is a fact to weigh.
- *WebDriver-level architecture:* no trace viewer, no network mocking, no video —
  anything CDP-ish you'd bolt on yourself through Selenium. If you need those, that's a
  real argument for Playwright.
- *Python only, and no built-in parallelism:* use pytest + pytest-xdist (it works —
  Selene is a library — but nothing is wired for you).
- *Safari only through Selenium's safaridriver configuration* — no special support.

## Summary matrix

✅ yes / ⚠️ partial or opt-in / ❌ no / — not claimed (see framework sections for
sources; "—" means we didn't verify a claim either way).

| Criterion | Selene | Selenide | SeleniumBase | Playwright | Cypress | Helium | Splinter | Pylenium | Selenium |
|---|---|---|---|---|---|---|---|---|---|
| Lazy re-resolution | ✅ | ✅ | ❌ | ✅ | ⚠️ | — | ❌ | ❌ | ❌ |
| Auto-wait on actions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| Retrying assertions | ✅ | ✅ | ⚠️ | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ❌ |
| Custom conditions API | ✅ | ✅ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ | ⚠️ |
| Collections wait | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Failure artifacts out of the box | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Own test runner | ❌ | ❌ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| WebDriver architecture | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Branded Safari | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ | — | ⚠️ | — | ✅ |

Notes: "WebDriver architecture" is a double-edged axis — ✅ means you can reuse Selenium
Grid, cloud providers and existing Selenium knowledge, ❌ means a purpose-built stack
(Playwright's toolchain, Cypress's in-browser run loop). ⚠️ for Safari means "possible
via the underlying Selenium driver, not specially documented".

## How to choose

- **You need trace viewer, network mocking, video, or maximum speed** → Playwright.
  It's the most complete toolchain in 2026; give it its due.
- **Your team is JS/TS-native and wants in-browser time-travel debugging** → Cypress —
  accepting its documented trade-offs (single browser, single superdomain, JS only).
- **You need W3C WebDriver infrastructure** (Selenium Grid, cloud device farms,
  multi-language teams) → Selenium or any wrapper on it.
- **You want Python + Selenium + maximum batteries** (recorder, dashboard, reports) →
  SeleniumBase.
- **You want a minimal thin API or label-based scripts** → Splinter or Helium.
- **You want Selenide-style "tests as prose" in Python**: lazy elements you can store,
  every line waiting, conditions as a composable API, on top of the standard WebDriver
  ecosystem → that's Selene 2.0. That's us. If the honest limitations above didn't
  scare you off — welcome. 🙂

## Sources

All accessed 2026-11-08.

[selenium-webdriver]: https://www.selenium.dev/documentation/webdriver/
[selenium-manager]: https://www.selenium.dev/documentation/selenium_manager/
[selenium-waits]: https://www.selenium.dev/documentation/webdriver/waits/
[selenium-browsers]: https://www.selenium.dev/documentation/webdriver/browsers/
[splinter-docs]: https://splinter.readthedocs.io/en/latest/
[splinter-api]: https://splinter.readthedocs.io/en/latest/api/driver-and-element-api.html
[splinter-src]: https://github.com/cobrateam/splinter/blob/master/splinter/driver/webdriver/__init__.py
[splinter-screenshots]: https://github.com/cobrateam/splinter/blob/master/docs/screenshot.rst
[helium-readme]: https://github.com/mherrmann/helium
[seleniumbase-readme]: https://github.com/seleniumbase/SeleniumBase
[seleniumbase-recorder]: https://github.com/seleniumbase/SeleniumBase/blob/master/help_docs/recorder_mode.md
[seleniumbase-deps]: https://github.com/seleniumbase/SeleniumBase/blob/master/requirements.txt
[pylenium-readme]: https://github.com/ElSnoMan/pyleniumio
[selenide-site]: https://selenide.org/
[selenide-readme]: https://github.com/selenide/selenide
[selenide-screenshots]: https://selenide.org/documentation/screenshots.html
[cypress-why]: https://docs.cypress.io/app/get-started/why-cypress
[cypress-retry]: https://docs.cypress.io/app/core-concepts/retry-ability
[cypress-tradeoffs]: https://docs.cypress.io/app/references/trade-offs
[cypress-cross]: https://docs.cypress.io/app/guides/cross-browser-testing
[playwright-home]: https://playwright.dev/python/
[playwright-locators]: https://playwright.dev/python/docs/locators
[playwright-assertions]: https://playwright.dev/python/docs/test-assertions
[playwright-assertions-node]: https://playwright.dev/docs/test-assertions
[playwright-locator-api]: https://playwright.dev/python/docs/api/class-locator
[playwright-trace]: https://playwright.dev/python/docs/trace-viewer
[playwright-mock]: https://playwright.dev/python/docs/mock
[playwright-runners]: https://playwright.dev/python/docs/test-runners
[playwright-browsers]: https://playwright.dev/python/docs/browsers
[playwright-grid]: https://playwright.dev/python/docs/selenium-grid
[selene-readme]: https://github.com/yashaka/selene/blob/selene-2.0.0rc10%2B/README.md
[selene-config]: https://github.com/yashaka/selene/blob/selene-2.0.0rc10%2B/selene/core/configuration.py

Registry data: PyPI JSON API (`pypi.org/pypi/<pkg>/json`), npm registry
(`registry.npmjs.org/cypress`), GitHub releases/API for Selenide and all repositories.
Code-level facts for Selene verified against the `selene-2.0.0rc10+` branch on
2026-11-08; the full research dossier is kept in issue #474.
