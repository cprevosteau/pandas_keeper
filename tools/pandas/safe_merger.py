import pandas as pd
from tools import LOGGER
from tools.pandas.assert_check import assert_column_values, assert_type, replace_check

SIDES = ["left", "right"]


def _to_list(val):
    if type(val) == list:
        return val
    return [val]


def _make_check_na_allowed(na_allowed_arg, keys):
    """Make a `na_allowed` of the form key_column -> is_na_allowed (bool)."""
    if isinstance(na_allowed_arg, bool):
        na_allowed = {key: na_allowed_arg for key in keys}
    else:
        na_allowed = na_allowed_arg
    assert isinstance(na_allowed, dict), "na_allowed must be a boolean or a dictionary."
    assert set(na_allowed.keys()) == set(keys), \
        "na_allowed must have the same keys as keys_dtypes"
    return na_allowed


def _check_keys_in_df(df, keys):
    diff_keys = list(set(keys) - set(df.columns))
    assert len(diff_keys) == 0, "These key columns are not present in df: %s" % diff_keys


def _check_keys_are_in_df_only_once(df, keys):
    col_times = df.columns[df.columns.isin(keys)].value_counts()
    wrong_cols = list(col_times[col_times > 1].index)
    assert len(wrong_cols) == 0, \
        "These column names match multiple columns each: %s" % wrong_cols


def _check_key_columns_have_the_right_types_and_missing_values(df, keys, dtypes, na_allowed):
    for col, dtype, na in [(key, dtypes[key], na_allowed[key]) for key in keys]:
        assert_type(df, col, dtype, na)


def _check_key_columns(df, keys, dtypes, na_allowed):
    """Check the key columns of df.

    Checks done:
        - key columns are to be presend in df
        - key columns must have a unique name or only be present once in df
        - Each key column must have the expected dtype and the presence of N/A values
          might be checked depending on na_allowed.

    """
    _check_keys_in_df(df, keys)
    _check_keys_are_in_df_only_once(df, keys)
    _check_key_columns_have_the_right_types_and_missing_values(
        df, keys, dtypes, na_allowed)


def _get_left_right_keys(on_key_dtypes, on, left_on, right_on):
    """Get right key columns and left key columns depending on the values of the arguments `on`,
     `left_on` and `right_on`.

    If none of `on`, `left_on` and `right_on` are specified, `on` will be set with keys of
    `keys_dtypes`. If only one key column is set and the argument `right_on` is used, `left_on`
    do not have to be specified. It will be set to this key column.

    """
    if type(on_key_dtypes) == dict:
        keys = list(on_key_dtypes.keys())
        assert on is None, \
            "If on_key_dtypes is specified with a dict," \
            " on should not be specified because it is redundant."
        if left_on is not None:
            assert right_on is not None, "left_on and right on should be specified together."
            left_on = _to_list(left_on)
            right_on = _to_list(right_on)
            assert len(left_on) == len(right_on), "left_on and right_on should have the same size."
            assert len(keys) == len(left_on), \
                "on_key_dtypes should have the same size as left_on and right_on."
            keys_is_left_keys = set(keys) == set(left_on)
            keys_is_right_keys = set(keys) == set(right_on)
            assert keys_is_left_keys or keys_is_right_keys,\
                "on_key_dtypes keys should correspond to either left_on or right_on."
            if keys_is_right_keys:
                left_key_dtypes = {left_on[idx]: on_key_dtypes[right_key]
                                   for idx, right_key in enumerate(right_on)}
            else:
                left_key_dtypes = on_key_dtypes
        else:
            assert right_on is None, "left_on and right on should be specified together."
            left_on = keys
            right_on = keys
            left_key_dtypes = on_key_dtypes
    else:
        if on is not None:
            assert left_on is None, "left_on should be None if on is not."
            assert right_on is None, "right_on should be None if on is not."
            on = _to_list(on)
            left_on = on
            right_on = on
        else:
            assert left_on is not None, "left_on should be specified if on is not."
            assert right_on is not None, "left_on should be specified if on is not."
            left_on = _to_list(left_on)
            right_on = _to_list(right_on)
            assert len(left_on) == len(right_on), "left_on and right_on should have the same size."
        left_key_dtypes = {key: on_key_dtypes for key in left_on}
    return left_key_dtypes, left_on, right_on


def _check_side_non_key_columns(df, other_df, keys, df_side):
    other_side = (set(SIDES) - {df_side}).pop()
    df_non_key_cols = set(df.columns) - set(keys)
    df_common_cols = set(other_df.columns) & df_non_key_cols
    assert len(df_common_cols) == 0, "The %s DataFrame non key columns should not have " \
        "these columns in common with columns of the %s DataFrame: %s" % (
        df_side, other_side, list(df_common_cols))


def _check_right_key_values_unicity(right_concat_keys):
    val_key = right_concat_keys.value_counts(dropna=False)
    wrong_keys = list(val_key[val_key > 1].index)
    assert len(
        wrong_keys) == 0, "Each of these key values are present on multiple rows: %s" % wrong_keys


def _get_matching_keys_info(concat_keys, other_concat_keys):
    isin = concat_keys.isin(other_concat_keys)
    return isin.sum(), isin.shape[0], isin.mean() * 100


def _drop_right_key_columns(df, left_keys, right_keys):
    key_cols_to_drop = list(set(right_keys) - set(left_keys))
    return df.drop(columns=key_cols_to_drop)


def safe_merge(left_df, right_df, how, on_keys_dtypes="str", on=None, left_on=None, right_on=None,
               na_allowed=None,
               left_na_allowed=None, right_na_allowed=None, unique_right=True, keep_left_keys=True,
               keep_right_keys=False)

# def _check_unicity_and_matching_key_values(left_df, right_df, left_keys, right_keys, unique_right):
#     """Check unicity and matching of key values.
#
#     If unique_right is True, assert that each concatenation of the key column values are unique in the right DataFrame.
#     Log the proportion of matching key values in the right and the left DataFrames.
#
#     """
#     right_concat_keys = pd.Series(list(zip(*[other[col] for col in right_keys])))
#     left_concat_keys = pd.Series(list(zip(*[self.df[col] for col in left_keys])))
#     if unique_right:
#         val_key = right_concat_keys.value_counts(dropna=False)
#         wrong_keys = list(val_key[val_key > 1].index)
#         assert len(
#             wrong_keys) == 0, "Each of these key values are present on multiple rows: %s" % wrong_keys
#     left_isin = left_concat_keys.isin(set(right_concat_keys))
#     right_isin = right_concat_keys.isin(set(left_concat_keys))
#     LOGGER.info("Left key values in right table: %s / %s, %.2f%%" % (
#         left_isin.sum(), left_isin.shape[0], left_isin.mean() * 100))
#     LOGGER.logger.info("Right key values in left table: %s / %s, %.2f%%" % (
#         right_isin.sum(), right_isin.shape[0], right_isin.mean() * 100))
#

#
# def merge(self, other, how="inner", on=None, left_on=None, right_on=None, na_allowed=False,
#           unique_right=True, keep_right_keys=False):
#     """Merge other with df.
#
#     Args:
#         other (DataFrame): right DataFrame to merge.
#         how (str, default: "inner"): how argument of pandas.merge
#         on, left_on, right_on (str or list): on, right_on, left_on arguments of pandas.merge
#                                             If none of `on`, `left_on` and `right_on` are specified, `on` will be set with keys of `keys_dtypes`.
#                                             If only one key column is set and the argument `right_on` is used, `left_on` do not have to be specified.
#                                             It will be set to this key column.
#                                             If right_on is specified, right key columns not in left_on are dropped
#                                             in the resulting DataFrame.
#         na_allowed (bool or dict, default: False): Are N/A values allowed in the right key columns ?
#                                    If it is a dict, must be of the form: key_column -> na_allowed.
#         unique_right (bool, default: True): Must the concatenation of right key column values unique in the right DataFrame ?
#         keep_right_keys (bool, default: False): Should the resulting DataFrame contain right key columns with different
#                                   column names than the left key columns ?
#
#     """
#     left_keys, right_keys = self._check_get_right_left_keys(other, on, left_on, right_on)
#     right_dtypes = {right_keys[i]: self.dtypes[l_key] for i, l_key in enumerate(left_keys)}
#     right_na_allowed = self._make_check_na_allowed(na_allowed, right_keys)
#     self._check_key_columns(other, right_keys, right_dtypes, right_na_allowed)
#     self._check_non_key_columns(other, left_keys, right_keys)
#     self._check_unicity_and_matching_key_values(other, left_keys, right_keys, unique_right)
#     self.df = self.df.merge(other, left_on=left_keys, right_on=right_keys, how=how)
#     if not keep_right_keys:
#         self._drop_right_key_columns(left_keys, right_keys)
#     return self


class SafeDF(object):

    def __init__(self, df, keys_dtypes, na_allowed=False):
        self.df = df
        self.dtypes = keys_dtypes
        self._keys = list(self.dtypes.keys())
        self.na_allowed = _make_check_na_allowed(na_allowed, self._keys)
        _check_key_columns(self.df, self._keys, self.dtypes, self.na_allowed)


# class SafeMerger(object):
#     """Test two DataFrames before merging them.
#
#     Checks done:
#         - key columns are to be present in right and left DataFrames
#         - key columns must have a unique name or only be present once in each DataFrame
#         - Each key column must have the expected dtype and the presence of N/A values
#           might be checked depending on na_allowed.
#         - Left and right DataFrames must not have columns in common except key columns from both.
#         - If unique_right, each concatenation of the key column values are unique in the right
#           DataFrame.
#
#     Args:
#         df (DataFrame): initial left DataFrame to merge.
#         keys_dtypes (dict): Dictionary of the form column_name -> dtype, where column_name
#             is to be used as a key for merging.
#         na_allowed (bool or dict, default: False): Are N/A values allowed ? If it is a dictionary,
#             must be of the form key_column -> bool.
#
#     """
#
#     def __init__(self, df, keys_dtypes, na_allowed=False):
#         self.na_allowed = self._make_check_na_allowed(na_allowed, self._keys)
#         self.dtypes = keys_dtypes
#         self._keys = list(self.dtypes.keys())
#         self.df = df
#         self._check_key_columns(self.df, self._keys, self.dtypes, self.na_allowed)






# def safe_merge(df, other, keys_dtypes, how="inner", on=None, left_on=None, right_on=None,
#                na_allowed=None,
#                left_na_allowed=None, right_na_allowed=None, unique_right=True, keep_left_keys=True,
#                keep_right_keys=False):
#     """Merge safely two DataFrames.
#
#     Checks done:
#         - key columns are to be present in right and left DataFrames
#         - key columns must have a unique name or only be present once in each DataFrame
#         - Each key column must have the expected dtype and the presence of N/A values
#           might be checked depending on na_allowed.
#         - Left and right DataFrames must not have columns in common except key columns from both.
#         - If unique_right, each concatenation of the key column values are unique in the right DataFrame.
#
#     Args:
#         df (DataFrame): left DataFrame to merge.
#         other (DataFrame): right DataFrame to merge.
#         keys_dtypes (dict): Dictionary of the form column_name -> dtype, where column_name
#             is to be used as a key for the merging.
#         how (str, default: "inner"): how argument of pandas.merge
#         on, left_on, right_on (str or list): on, right_on, left_on arguments of pandas.merge
#             If none of `on`, `left_on` and `right_on` are specified, `on` will be set with keys of `keys_dtypes`.
#             If only one key column is set and the argument `right_on` is used, `left_on` do not have to be specified.
#             It will be set to this key column.
#             If right_on is specified, right key columns not in left_on are dropped
#             in the resulting DataFrame.
#         na_allowed (bool or dict, default: None): Are N/A values allowed in the key columns ?
#             If it is a dict, must be of the form: key_column -> na_allowed.
#         left_na_allowed (bool or dict, default: None): Are N/A values allowed in the left key columns ?
#             False if it is None.
#             If it is a dict, must be of the form: key_column -> na_allowed.
#         right_na_allowed (bool or dict, default: None): Are N/A values allowed in the right key columns ?
#             False if it is None.
#             If it is a dict, must be of the form: key_column -> na_allowed.
#         unique_right (bool, default: True): Must the concatenation of right key column values unique in the right DataFrame ?
#
#     """
#     if na_allowed is not None:
#         assert left_na_allowed is None and right_na_allowed is None, "left_na_allowed or right_na_allowed must not be specified if na_allowed is."
#         left_na_allowed = na_allowed
#         right_na_allowed = na_allowed
#     else:
#         if left_na_allowed is None:
#             left_na_allowed = False
#         if right_na_allowed is None:
#             right_na_allowed = False
#     return (SafeMerger(df, keys_dtypes, left_na_allowed)
#             .merge(other, how, on, left_on, right_on, right_na_allowed, unique_right,
#                    keep_right_keys)
#             .df)
