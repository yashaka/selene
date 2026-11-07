# TINYMCE_URL = 'https://www.tiny.cloud/docs/tinymce/latest/cloud-quick-start/'
import os
from pathlib import Path

import tests

TINYMCE_URL = os.getenv('TINYMCE_URL', 'http://127.0.0.1:8000/demo/tinymce')
# local-run default = the demo app origin (owner can enable Pages there); in CI it is
# overridable per repo via GitHub Actions variable TODOMVC4TASJ_URL, else derived from pipeline actor
TODOMVC4TASJ_URL = (
    os.getenv('TODOMVC4TASJ_URL') or 'https://yashaka.github.io/todomvc4tasj/home.html'
)
# SELENOID_HOST = 'selenoid.autotests.cloud'
SELENOID_HOST = 'selenoid.autotest.how'
LOGO_PATH = str(Path(tests.__file__).parent.parent / 'docs/assets/images/logo-icon.png')
