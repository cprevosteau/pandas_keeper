from typing import Sized, Dict, Union, Optional
import pandas as pd
from pandas import DataFrame, Series


def _assert_empty_wrong_values(wrong_values: Sized, msg: str) -> None:
    assert len(wrong_values) == 0, msg


def assert_values(pds, values):
    """Assert that the column has values among expected ones.

    Args:
        pds (Series): Series to be checked.
        values (set, list-like): Values allowed to be found in the Series. N/A value are ignored.
    """
    nn_col = pds[pds.notnull()]
    nn_col_in = nn_col.isin(values)
    wrong_values = set(nn_col[~nn_col_in])
    _assert_empty_wrong_values(wrong_values,
                               "These values should not be present in the pandas Series %s: %s" %
                               (pds.name, wrong_values))


def safe_replace(df: DataFrame, values: Dict[str, Dict],
                 strip: Union[bool, Dict[str, bool]] = True,
                 lower: Union[bool, Dict[str, bool]] = False,
                 inplace: bool = False):
    """Replace values in the dataframe and check that values are among the expected ones.

    Args:
        df (DataFrame): DataFrame having columns values to be replaced.
        values (dict of str, dict): Dictionary which for each key column name has a replacement
            dictionary of the form old_value -> new value. Once the replacement has taken place,
            the values of the resulting column is expecting to take values only in the new values of
            the replacement dictionary.
        strip (bool, default: True): Should the string values be stripped before replacing values ?
        lower (bool, default: False): Should the string values be lowered before replacing values ?
        inplace (bool):
    """
    if not inplace:
        df = df.copy()
    if isinstance(strip, bool):
        strip = {col: strip for col in values}
    if isinstance(lower, bool):
        lower = {col: lower for col in values}
    with pd.option_context('mode.chained_assignment', None):
        for col, replace_dic in values.items():
            safe_replace_series(df[col], replace_dic, strip[col], lower[col], inplace=True)
    return df


def safe_replace_series(pds: Series, values: Dict, strip: bool = True,
                        lower: bool = False, inplace=False) -> Optional[Series]:
    if not inplace:
        pds = pds.copy()
    if strip and pds.dtype == "object":
        str_idx = pds.map(lambda x: isinstance(x, str))
        pds.loc[str_idx] = pds.loc[str_idx].str.strip()
    if lower and pds.dtype == "object":
        str_idx = pds.map(lambda x: isinstance(x, str))
        pds.loc[str_idx] = pds.loc[str_idx].str.lower()
        values = {k.lower(): v for k, v in values.items()}
    pds.replace(values, inplace=True)
    assert_values(pds, values.values())
    if not inplace:
        return pds
    return None


def assert_non_null_idx(pds: Series, na_allowed: bool,
                        return_value: bool = False) -> Optional[Series]:
    nn_idx = pds.notnull()
    if not na_allowed:
        assert nn_idx.min() == 1, "The Series %s should not have null values." % pds.name
    if return_value:
        return nn_idx
    return None


def assert_type(pds, dtype, na_allowed):
    """Assert that the column has values of the expected type.

    Args:
        pds (Series): Series to be checked.
        dtype (dtype): Type expected to be found in the column values.
        na_allowed (bool): Are N/A values allowed ?

    """
    non_null_idx = assert_non_null_idx(pds, na_allowed, return_value=True)
    nn_col = pds[non_null_idx]
    wrong_values = set(nn_col[nn_col != nn_col.astype(dtype)])
    _assert_empty_wrong_values(wrong_values,
                               "The Series %s has value(s) of a type different from %s: %s" %
                               (pds.name, dtype, wrong_values))
