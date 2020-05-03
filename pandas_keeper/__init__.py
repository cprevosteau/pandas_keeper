from pandas.core.frame import DataFrame, Series
from .assert_check import assert_type, assert_values, safe_replace, safe_replace_series
from .safe_merger import safe_merge


def patch_pandas():
    # Monkey patch pandas
    DataFrame.safe_merge = safe_merge
    DataFrame.safe_replace = safe_replace
    Series.assert_values = assert_values
    Series.assert_type = assert_type
    Series.safe_replace = safe_replace_series
