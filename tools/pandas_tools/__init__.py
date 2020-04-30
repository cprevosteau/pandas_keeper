from pandas.core.frame import DataFrame, Series
from .safe_merger import safe_merge
from .assert_check import assert_type, assert_values, safe_replace


def patch_pandas():
    # Monkey patch pandas
    DataFrame.safe_merge = safe_merge
    DataFrame.safe_replace = safe_replace
    Series.assert_values = assert_values
    Series.assert_type = assert_type
