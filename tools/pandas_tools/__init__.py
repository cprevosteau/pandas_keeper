from pandas.core.frame import DataFrame
from .safe_merger import safe_merge


def patch_pandas():
    # Monkey patch DataFrame
    DataFrame.safe_merge = safe_merge

