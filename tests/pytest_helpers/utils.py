from functools import wraps
import pytest


def assert_error(func):

    @wraps(func)
    def decorator(*args, **kw):
        assert "should_fail" in kw, \
            "To use assert_error decorator, the function must be decorated with " \
            "pytest.mark.parametrize which must provide should_fail as argument."
        expected_assert_error = kw["should_fail"]
        if expected_assert_error is True:
            expected_assert_error = AssertionError
        if expected_assert_error:
            with pytest.raises(expected_assert_error):
                func(*args, **kw)
        else:
            func(*args, **kw)
    return decorator
