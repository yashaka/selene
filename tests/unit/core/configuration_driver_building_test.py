from types import SimpleNamespace

import pytest

from selene.core.configuration import (
    Config,
    _build_local_driver_by_name_or_remote_by_url_and_options,
)


@pytest.mark.parametrize(
    "driver_name, expected_name",
    [
        ("chrome", "chrome"),
        ("firefox", "firefox"),
        ("edge", "msedge"),
    ],
)
def test_build_local_driver_by_name_routes_to_expected_webdriver(
    monkeypatch, driver_name, expected_name
):
    import selenium.webdriver as webdriver_module
    import selenium.webdriver.chrome.service as chrome_service_module
    import selenium.webdriver.firefox.service as firefox_service_module
    import selenium.webdriver.edge.service as edge_service_module

    monkeypatch.setattr(
        webdriver_module,
        "Chrome",
        lambda **kwargs: SimpleNamespace(name="chrome", kwargs=kwargs),
    )
    monkeypatch.setattr(
        webdriver_module,
        "Firefox",
        lambda **kwargs: SimpleNamespace(name="firefox", kwargs=kwargs),
    )
    monkeypatch.setattr(
        webdriver_module,
        "Edge",
        lambda **kwargs: SimpleNamespace(name="msedge", kwargs=kwargs),
    )

    monkeypatch.setattr(
        chrome_service_module,
        "Service",
        lambda *args, **kwargs: SimpleNamespace(kind="chrome-service"),
    )
    monkeypatch.setattr(
        firefox_service_module,
        "Service",
        lambda *args, **kwargs: SimpleNamespace(kind="firefox-service"),
    )
    monkeypatch.setattr(
        edge_service_module,
        "Service",
        lambda *args, **kwargs: SimpleNamespace(kind="edge-service"),
    )

    built_driver = _build_local_driver_by_name_or_remote_by_url_and_options(
        Config(driver_name=driver_name)
    )

    assert built_driver.name == expected_name
