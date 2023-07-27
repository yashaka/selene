# MIT License
#
# Copyright (c) 2023 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from webdriver_manager.chrome import ChromeDriverManager


def _to_find_chromedrivers_from_115(driver_manager: ChromeDriverManager):
    """
    Fixes webdriver_manager 3.8.6 issue with latest chrome versions (>= 115.0.5763.0)
    See https://github.com/SergeyPirogov/webdriver_manager/issues/536

    Will work for any version of webdriver_manager >= 3.8.6,
    but actually, only 3.8.6 is affected by patching.

    Fix is based on simple ideas from:
    * https://github.com/SergeyPirogov/webdriver_manager/issues/536#issuecomment-1641266654
    * https://github.com/SergeyPirogov/webdriver_manager/issues/536#issuecomment-1641396604

    It monkey patches all driver_manager inner objects (including nested ones)
    and methods

    But also for newer versions of Chrome browsers – it patches PATTERN dict
    from wdm utils.
    This PATTERN patching is the most risky part of the fix,
    because it changes the whole library behavior,
    not just the object passed to this function.
    Let's keep fingers crossed;p
    """
    import webdriver_manager

    if webdriver_manager.__version__ != '3.8.6':
        return driver_manager

    from webdriver_manager.core import logger as wdm_logger
    from packaging import version
    from webdriver_manager.core import utils as wdm_utils
    from webdriver_manager.core.utils import ChromeType

    # We alias driver object from driver_manager as driver_utils
    # for lesser confusion.
    # In fact wdm driver object is more a bunch of utility functions.
    # From OOP perspective,
    # it's not a pure object representing actual "low level driver binary".
    # And 'driver' name also conflicts with common 'driver' client object from selenium.
    driver_utils = driver_manager.driver
    http_client = driver_utils._http_client

    def chrome_apis_url(endpoint):
        return f'https://googlechromelabs.github.io/chrome-for-testing/{endpoint}'

    good_binary_version = None
    good_binary_url = None
    installed_browser_version = driver_utils.get_browser_version_from_os()

    if installed_browser_version:
        if version.parse(installed_browser_version) < version.parse('115.0.5763.0'):
            # if browser version is less than 115.0.5763.0
            # then we use old wdm logic
            # and just return the driver_manager as is
            return driver_manager

        # patching wdm_utils.PATTERN
        # we need all 4 sub-versions not just 3 of them
        wdm_utils.PATTERN[ChromeType.GOOGLE] = r"\d+\.\d+\.\d+.\d+"
        # retaking version from os after patched pattern
        good_binary_version = wdm_utils.get_browser_version_from_os(
            driver_utils.get_browser_type()
        )
        # let's reset _browser_version to the new 4-sub-versions value
        # from here, we assume that
        # "good" binary version is the same as "good" browser version
        driver_utils._browser_version = good_binary_version

        known_good_versions = (
            http_client.get(chrome_apis_url('known-good-versions-with-downloads.json'))
            .json()
            .get('versions', [])
        )

        matched_version_downloads_chromedriver_per_platform: list = next(
            iter(
                info.get('downloads', {}).get('chromedriver', [])
                for info in known_good_versions
                if info.get('version', None) == good_binary_version
            ),
            [],
        )

        good_binary_url = next(
            iter(
                info.get('url', None)
                for info in matched_version_downloads_chromedriver_per_platform
                if info.get('platform') == driver_utils.get_os_type().replace('_', '-')
            ),
            None,
        )

    if (not installed_browser_version) or (not good_binary_url):
        wdm_logger.log(
            'Failed to get version of Chrome installed at your OS '
            f'(detected os type: {driver_utils._os_type}).'
            f'Going to install the chromedriver binary '
            f'matching latest known stable version of Chrome...'
        )
        last_known_good_versions_with_downloads = http_client.get(
            chrome_apis_url('last-known-good-versions-with-downloads.json')
        ).json()
        stable_channel = last_known_good_versions_with_downloads.get(
            'channels', {}
        ).get('Stable', {})

        # Above and below, we allways use get('key', default) instead of just ['key']
        # to provide default value in case of missing key
        # and make further processing easier and safer
        # (we don't need to check for None when processing via comprehensions).
        # Sometimes, like below we use `get('key', '') or None`
        # instead of just `get('key', None)` or even `get('key)`
        # in order to hint the type of result of the value by the key to get
        # (in this case - string by hinting it via default empty string '').
        # We could use just type hinting on a variable,
        # but we prefer the style consistent with other similar parts of this code...
        last_known_good_version = (stable_channel.get('version', '')) or None
        platform_and_url_pairs = stable_channel.get('downloads', {}).get(
            'chromedriver', []
        )
        url_where_platform_is_os_type = next(
            iter(
                # url is obviously a string and if absent we are interested in None
                # emphasizing this by providing it explicitly
                pair.get('url', None)
                for pair in platform_and_url_pairs
                # .get_os_type() may return None, hence '' as default in get is intended
                if pair.get('platform', '')
                == driver_utils.get_os_type().replace('_', '-')
            ),
            None,
        )
        wdm_logger.log(
            f'latest known stable version of Chrome: {last_known_good_version}'
        )

        good_binary_version = last_known_good_version
        good_binary_url = url_where_platform_is_os_type

    if good_binary_url:
        # it happened that we found good binary url on our own
        # let's monkey patch WDM classes and objects they know it too ;P

        # now we provide exactly correct and ready for download url
        driver_utils._url = good_binary_url

        # let's just return it as is
        driver_utils.get_driver_download_url = lambda: driver_utils._url

        # just in case...
        driver_utils._version = good_binary_version

        # new endpoints provide file for download differently,
        # old wdm filename logic just does not work
        # so let's patch it too
        class PatchedFile(wdm_utils.File):
            filename = good_binary_url.split('/')[-1]  # type: ignore

        # and use PatchedFile on download...
        def download_file(url: str):
            wdm_logger.log(f"About to download new driver from {url}")
            response = http_client.get(url)
            return PatchedFile(response)

        # – by download manager
        # (we safely patch only current object, not the whole class)
        driver_manager._download_manager.download_file = download_file

        # similar story with processing filenames logic...
        def get_binary(files, driver_name):
            try:
                return next(
                    file
                    for file in files
                    if driver_name in file.split('/')[-1].split('.')[0]
                )
            except Exception as e:
                raise Exception(
                    f"Can't find binary for {driver_name} among {files}"
                ) from e

        # safely patching only exactly our manager object's get_binary
        driver_manager.driver_cache._DriverCache__get_binary = get_binary

    return driver_manager
