import sys
import os.path as osp
import pytest
from functools import wraps
from inspect import signature, Parameter
sys.path.insert(0, osp.normpath(osp.join(osp.dirname(__file__), osp.pardir)))


def assert_error(func):

    @wraps(func)
    def decorator(*args, **kw):
        expected_assert_error = kw.pop("assert_error")
        print("BIEN RENTRÉ DANS DECORATOR")
        if expected_assert_error:
            with pytest.raises(AssertionError):
                func(*args, **kw)
        else:
            func(*args, **kw)

    sig = signature(func)
    assert_arg = Parameter("assert_error", Parameter.KEYWORD_ONLY)
    sig = sig.replace(parameters=tuple(sig.parameters.values()) + (assert_arg, ))
    decorator.__signature__ = sig

    return decorator
