import sys
import os.path as osp
import pytest
from functools import wraps
import pandas as pd
import numpy as np
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
        if expected_assert_error is True:
            expected_assert_error = AssertionError
        if expected_assert_error:
            with pytest.raises(expected_assert_error):
                func(*args, **kw)
        else:
            func(*args, **kw)
    return decorator


@pytest.helpers.register
def df_to_merge():
    df = pd.DataFrame({"float1": np.random.randn(20)})
    df["mult_int_key"] = list(range(10)) + list(range(10))
    df["int_key"] = range(20)
    df["mult_str_key"] = df["mult_int_key"].map(str)
    df["str_key"] = df["int_key"].map(str)
    df["str1"] = [chr(97 + i) for i in range(20)]
    df["int_key_with_nan"] = df["int_key"].map(lambda x: x if x % 2 else None)
    df["mult_col_int_key1"] = df["mult_col_int_key2"] = df["int_key"]
    df = df.rename(
        columns={"mult_col_int_key1": "mult_col_int_key", "mult_col_int_key2": "mult_col_int_key"})
    return df
