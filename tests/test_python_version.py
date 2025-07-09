import pytest
import sys

def test_python_version_support():
    # This test should fail if Python 3.8 is considered supported
    # and pass if it's not.
    # For now, we'll make it fail if the current Python version is 3.8
    # and pass if it's higher.
    # In a real scenario, this would check against the project's declared supported versions.
    assert sys.version_info.major == 3 and sys.version_info.minor > 8, \
        "Python 3.8 is still supported, but should be dropped."


