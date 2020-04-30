import pandas as pd
from .logger import Logger
from .assert_check import assert_type

SIDES = ["left", "right"]
LOGGER = Logger()


def safe_merge(left_df, right_df, how="left", on_key_dtypes="str", on=None, left_on=None,
               right_on=None, na_allowed=False, left_na_allowed=None, right_na_allowed=None,
               drop_side_keys="right", suffixes=(False, False), validate="many_to_one",
               logger=LOGGER.logger, **merge_kwargs):
    left_keys_dtypes, right_key_dtypes, left_keys, right_keys = _get_left_right_keys(
        on_key_dtypes, on, left_on, right_on)

    left_na_allowed, right_na_allowed = _get_check_na_allowed_args(
        na_allowed, left_na_allowed, right_na_allowed)

    left_na_allowed = _make_check_na_allowed(left_na_allowed, left_keys)
    right_na_allowed = _make_check_na_allowed(right_na_allowed, right_keys)

    _check_key_columns(left_df, left_keys, left_keys_dtypes, left_na_allowed)
    _check_key_columns(right_df, right_keys, right_key_dtypes, right_na_allowed)

    left_concat_keys = _concat_keys(left_df, left_keys)
    right_concat_keys = _concat_keys(right_df, right_keys)

    logger.info("Left key values in right table: %s / %s, %.2f%%" % _get_matching_keys_info(
        left_concat_keys, right_concat_keys))
    logger.info("Right key values in left table: %s / %s, %.2f%%" % _get_matching_keys_info(
        right_concat_keys, left_concat_keys))

    merged_df = left_df.merge(right_df, how=how, left_on=left_keys, right_on=right_keys,
                              suffixes=suffixes, validate=validate, **merge_kwargs)
    if drop_side_keys == "right":
        merged_df = _drop_other_key_columns(merged_df, left_keys, right_keys)
    elif drop_side_keys == "left":
        merged_df = _drop_other_key_columns(merged_df, right_keys, left_keys)
    return merged_df


def _to_list(val):
    if type(val) == list:
        return val
    return [val]


def _concat_keys(df, keys):
    return pd.Series(list(zip(*[df[col] for col in keys])))


def _get_check_na_allowed_args(na_allowed_arg, left_na_allowed_arg, right_na_allowed_arg):
    if na_allowed_arg is None:
        assert left_na_allowed_arg is not None and right_na_allowed_arg is not None, \
            "If na_allowed is None, left_na_allowed and right_na_allowed should be specified."
        return left_na_allowed_arg, right_na_allowed_arg
    assert left_na_allowed_arg is None and right_na_allowed_arg is None, \
        "If na_allowed is specified, left_na_allowed and right_na_allowed should not be specified."
    return na_allowed_arg, na_allowed_arg


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
        assert_type(df[col], dtype, na)


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
                right_key_dtypes = on_key_dtypes
            else:
                right_key_dtypes = {right_on[idx]: on_key_dtypes[left_key]
                                    for idx, left_key in enumerate(left_on)}
                left_key_dtypes = on_key_dtypes
        else:
            assert right_on is None, "left_on and right on should be specified together."
            left_on = keys
            right_on = keys
            left_key_dtypes = on_key_dtypes
            right_key_dtypes = on_key_dtypes
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
        right_key_dtypes = {key: on_key_dtypes for key in right_on}
    return left_key_dtypes, right_key_dtypes, left_on, right_on


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


def _drop_other_key_columns(df, keys, other_keys):
    key_cols_to_drop = list(set(other_keys) - set(keys))
    return df.drop(columns=key_cols_to_drop)
