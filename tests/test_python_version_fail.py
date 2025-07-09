import pytest
import sys

def test_python_38_not_supported():
    # This test should fail if Python 3.8 is detected.
    # It simulates the scenario where we want to drop support for Python 3.8.
    if sys.version_info.major == 3 and sys.version_info.minor == 8:
        pytest.fail("Python 3.8 is detected and should not be supported.")
    else:
        # For Python versions other than 3.8, the test should pass.
        assert sys.version_info.major == 3 and sys.version_info.minor >= 9, \
            "This test should only pass on Python 3.9 or higher, or fail on 3.8."


