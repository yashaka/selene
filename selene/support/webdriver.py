# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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
import warnings
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver


class Help:
    def __init__(self, driver: WebDriver):
        self._driver = driver

    def save_page_source(self, file: str) -> Optional[str]:
        if not file.lower().endswith('.html'):
            warnings.warn("name used for saved pagesource does not match file "
                          "type. It should end with an `.html` extension", UserWarning)

        html = self._driver.page_source

        try:
            with open(file, 'w', encoding="utf-8") as f:
                f.write(html)
        except IOError:
            return None
        finally:
            del html

        return file

    def save_screenshot(self, file: str) -> Optional[str]:
        if not file.lower().endswith('.png'):
            warnings.warn("name used for saved pagesource does not match file "
                          "type. It should end with an `.png` extension", UserWarning)

        return file if self._driver.get_screenshot_as_file(file) else None
