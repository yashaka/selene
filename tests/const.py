# TINYMCE_URL = 'https://www.tiny.cloud/docs/tinymce/latest/cloud-quick-start/'
from pathlib import Path

import tests

TINYMCE_URL = 'https://autotest.how/demo/tinymce'
# SELENOID_HOST = 'selenoid.autotests.cloud'
SELENOID_HOST = 'selenoid.autotest.how'
LOGO_PATH = str(Path(tests.__file__).parent.parent / 'docs/assets/images/logo-icon.png')
