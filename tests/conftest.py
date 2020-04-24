import sys
import os.path as osp
import pytest
from functools import wraps
sys.path.insert(0, osp.normpath(osp.join(osp.dirname(__file__), osp.pardir)))

pytest_plugins = ['helpers_namespace']


@pytest.helpers.register
def assert_error(func):

    @wraps(func)
    def decorator(*args, **kw):
        assert "should_fail" in kw, \
            "To use assert_error decorator, the function must be decorated with " \
            "pytest.mark.parametrize which must provide should_fail as argument."
        expected_assert_error = kw["should_fail"]
        if expected_assert_error:
            with pytest.raises(AssertionError):
                func(*args, **kw)
        else:
            func(*args, **kw)
    return decorator
