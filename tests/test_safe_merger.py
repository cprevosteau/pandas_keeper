import pytest
import pandas as pd
from pytest_helpers.utils import assert_error
from pandas_keeper.safe_merger import _make_check_na_allowed, _check_keys_in_df, \
    _check_keys_are_in_df_only_once, _get_left_right_keys, _check_side_non_key_columns, \
    _check_right_key_values_unicity, _get_matching_keys_info, _drop_other_key_columns, \
    _get_check_na_allowed_args, safe_merge


@pytest.mark.parametrize("left_columns, right_columns, kw, final_columns, should_fail, "
                         "case", [
    (["int_key", "str1"], ["int_key", "str_key"], {"on_key_dtypes": {"int_key": "int"}},
     ["int_key", "str1", "str_key"], False, "normal case"),
    (["int_key", "str1"], ["str_key"], {"left_on": "int_key", "right_on": "str_key"}, None, True,
     "int_key is not a string error."),
    (["int_key", "str1", "int_key"], ["int_key", "str_key"], {"on_key_dtypes": {"int_key": "int"}},
     None, True, "duplicate_key_column"),
    (["int_key", "str1"], ["int_key", "str1"],
     {"on_key_dtypes": {"int_key": "int"}, "suffixes": (False, False)},
     None, ValueError, "Overlaping columns"),
    (["int_key", "str1"], ["mult_int_key", "str_key"],
     {"on_key_dtypes": "int", "left_on": "int_key", "right_on": "mult_int_key",
      "validate": "many_to_one"}, None, pd.errors.MergeError, "Not many to one"),
    (["int_key_with_nan", "str1"], ["mult_int_key", "str_key"],
     {"on_key_dtypes": "int", "left_on": "int_key_with_nan", "right_on": "mult_int_key",
      "na_allowed": False}, None, True, "NA in left keys.")
 ])
@assert_error
def test_safe_merger(df_to_merge, left_columns, right_columns, kw, final_columns, should_fail,
                     case):
    # Given
    left_df = df_to_merge[left_columns]
    right_df = df_to_merge[right_columns]

    # When
    final_df = safe_merge(left_df, right_df, **kw)

    # Then
    if not should_fail:
        assert set(final_df.columns) == set(final_columns)


@pytest.mark.parametrize("na_allowed_arg, keys, expected_na_allowed, should_fail, case", [
    (True, ["a", "b"], {"a": True, "b": True}, False, "na_allowed is True"),
    (False, ["a", "b"], {"a": False, "b": False}, False, "na_allowed is False"),
    ({"a": True, "b": False}, ["a", "b"], {"a": True, "b": False}, False,
     "na_allowed is a dict with the rights keys"),
    (list("erreur"), ["a", "b"], None, True,
     "na_allowed is not a dict or a bool, so it should fail"),
    ({"a": True}, ["a", "b"], None, True,
     "na_allowed does not contain all the keys so it should fail")
])
@assert_error
def test_make_check_na_allowed(na_allowed_arg, keys, expected_na_allowed, should_fail,
                               case):
    # When
    actual_na_allowed = _make_check_na_allowed(na_allowed_arg, keys)

    # Then
    if not should_fail:
        assert actual_na_allowed == expected_na_allowed


@pytest.mark.parametrize("na_allowed_arg, left_na_allowed_arg, right_na_allowed_arg, "
                         "expected_left_na_allowed, expected_right_na_allowed, should_fail, case", [
                             (True, None, None, True, True, False,
                              "Only na_allowed is spedcified with a boolean."),
                             (None, True, False, True, False, False,
                              "Left na_allowed and right_na_allowed are specified"),
                             ({"test": True}, {"error": True}, None, None, None, True,
                              "na_allowed and left_na_allowed should not be specified together."),
                             ({"test": True}, None, {"error": True}, None, None, True,
                              "na_allowed and right_na_allowed should not be specified together."),
                             (None, None, {"error": True}, None, None, True,
                              "right_na_allowed should not be specified alone."),
                             (None, {"error": True}, None, None, None, True,
                              "left_na_allowed should not be specified alone.")
                         ])
@assert_error
def test_get_check_na_allowed_args(na_allowed_arg, left_na_allowed_arg, right_na_allowed_arg,
                                   expected_left_na_allowed, expected_right_na_allowed, should_fail,
                                   case):
    # When
    actual_left_na_allowed, actual_right_na_allowed = _get_check_na_allowed_args(
        na_allowed_arg, left_na_allowed_arg, right_na_allowed_arg)

    # Then
    if not should_fail:
        assert actual_left_na_allowed == expected_left_na_allowed
        assert actual_right_na_allowed == expected_right_na_allowed


@pytest.mark.parametrize("df, keys, should_fail, case", [
    (pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["a", "b"], False, "keys are present in df"),
    (pd.DataFrame({"a": [1], "b": [2], "c": [3]}), ["a", "d"], True,
     "key d is not present in df")
])
@assert_error
def test_check_key_columns_in_df(df, keys, should_fail, case):
    # When/Then it should fail depending on should_fail
    _check_keys_in_df(df, keys)


@pytest.mark.parametrize("df, keys, should_fail, case", [
    (pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"]), ["a", "b"], False,
     "keys are present only once in df"),
    (pd.DataFrame([[1, 2, 3, 4]], columns=["a", "b", "b", "d"]), ["a", "b"], True,
     "The key column b is present more than once."),
])
@assert_error
def test_check_keys_are_in_df_only_once(df, keys, should_fail, case):
    # When/Then it should fail depending on should_fail
    _check_keys_are_in_df_only_once(df, keys)


@pytest.mark.parametrize("on_key_dtypes, on, left_on, right_on, expected_left_key_dtypes, "
    "expected_right_key_dtypes, expected_left_keys, expected_right_keys, should_fail, case", [  # noqa
    ({"a": "str", "b": "int"}, None, None, None, {"a": "str", "b": "int"}, {"a": "str", "b": "int"},
     ["a", "b"], ["a", "b"], False, "on_key_dtypes is specified with a dict"),
    ("int", ["a", "b"], None, None, {"a": "int", "b": "int"}, {"a": "int", "b": "int"}, ["a", "b"],
     ["a", "b"], False, "on is specified with a list of column and on_key_dtypes with a dtype"),
    ("str", "a", None, None, {"a": "str"}, {"a": "str"}, ["a"], ["a"], False,
     "on is specified with a column"),
    ("str", None, ["a", "b"], ["a", "d"], {"a": "str", "b": "str"}, {"a": "str", "d": "str"},
     ["a", "b"], ["a", "d"], False, "left_on and right_on are specified with list of columns"),
    ("str", None, "b", "d", {"b": "str"}, {"d": "str"}, ["b"], ["d"], False,
     "left_on and right_on are specified with a column"),
    ({"b": "str", "a": "int"}, None, ["a", "b"], ["a", "d"], {"a": "int", "b": "str"},
     {"a": "int", "d": "str"}, ["a", "b"], ["a", "d"], False,
     "on_keys_dtype with left_on columns, left_on and right_on are well specified"),
    ({"d": "str", "a": "int"}, None, ["a", "b"], ["a", "d"], {"a": "int", "b": "str"},
     {"a": "int", "d": "str"}, ["a", "b"], ["a", "d"], False,
     "on_keys_dtype with right_on columns, left_on and right_on are well specified"),
    ({"a": "str", "b": "int"}, ["a", "b"], None, None, None, None, None, None, True,
     "on_key_dtypes and on should not be specified together if on_key_dtypes is a dict."),
    ("int", ["a", "b"], "error", None, None, None, None, None, True,
     "on and left_on should not be specified together"),
    ("int", ["a", "b"], None, "error", None, None, None, None, True,
     "on and right_on should not be specified together"),
    ("int", None, "a", ["a", "b"], None, None, None, None, True,
     "left_on and right_on should have the same size"),
    ({"a": "str", "c": "int"}, None, ["a", "d"], ["a", "b"], None, None, None, None, True,
     "on_key_dtypes keys should correspond to either left_on columns or right_on columns."),
    ({"b": "int"}, None, ["a", "d"], ["a", "b"], None, None, None, None,
     True, "on_key_dtypes keys should correspond to either left_on columns or right_on columns.")])
@assert_error
def test_get_left_right_keys(on_key_dtypes, on, left_on, right_on, expected_left_key_dtypes,
                             expected_right_key_dtypes, expected_left_keys, expected_right_keys,
                             should_fail, case):
    # When
    actual_left_key_dtypes, actual_right_key_dtypes, actual_left_keys, actual_right_keys = \
        _get_left_right_keys(on_key_dtypes, on, left_on, right_on)

    # Then
    if not should_fail:
        assert actual_left_key_dtypes == expected_left_key_dtypes
        assert actual_right_key_dtypes == expected_right_key_dtypes
        assert actual_left_keys == expected_left_keys
        assert actual_right_keys == expected_right_keys


@pytest.mark.parametrize("columns, other_columns, keys, should_fail, case", [
    (["int_key", "str1"], ["int_key", "float1"], ["int_key"], False,
     "DataFrames have not non key columns in common."),
    (["int_key", "float1"], ["int_key", "float1"], ["int_key"], True,
     "Dataframes should not have non key columns in common."),
    (["int_key", "float1"], ["str_key", "str1"], ["int_key"], False,
     "DataFrames have not non key columns in common. 2"),
    (["int_key", "float1", "str_key"], ["str_key", "str1"], ["int_key"], True,
     "DataFrame have key from other on its non key columns.")
])
@assert_error
def test_check_left_non_key_columns(df_to_merge, columns, other_columns, keys, should_fail, case):
    # Given
    left_df = df_to_merge[columns]
    right_df = df_to_merge[other_columns]

    # When/Then it should fail depending on should_fail
    _check_side_non_key_columns(left_df, right_df, keys, "left")


@pytest.mark.parametrize(
    "right_keys, should_fail, case",
    [
        (["int_key"], False, "Each right key is unique."),
        (["mult_int_key"], True, "It should not be duplicate right key values."),
        (["int_key", "mult_str_key"], False, "Each right keys concatenation is unique."),
        (["mult_int_key", "mult_str_key"], True,
         "It should not be duplicate right keys concatenations."),
    ])
@assert_error
def test_check_right_key_values_unicity(df_to_merge, right_keys, should_fail, case):
    # Given
    right_concat_keys = pd.Series(list(zip(*[df_to_merge[col] for col in right_keys])))

    # When/Then it should fail depending on should_fail
    _check_right_key_values_unicity(right_concat_keys)


@pytest.mark.parametrize(
    "keys, other_keys, sum_in_other, size, pct_in_other",
    [
        (["int_key"], ["int_key"], 20, 20, 100.),
        (["int_key"], ["mult_int_key"], 10, 20, 50.),
        (["mult_int_key"], ["int_key"], 20, 20, 100.),
        (["int_key", "mult_int_key"], ["mult_int_key", "mult_int_key"], 10, 20, 50.)
    ])
def test_get_matching_keys_info(df_to_merge, keys, other_keys, sum_in_other, size, pct_in_other):
    # Given
    concat_keys = pd.Series(list(zip(*[df_to_merge[col] for col in keys])))
    other_concat_keys = pd.Series(list(zip(*[df_to_merge[col] for col in other_keys])))

    # When
    actual_sum_in_other, actual_size, actual_pct_in_other = _get_matching_keys_info(
        concat_keys, other_concat_keys)

    # Then
    assert actual_sum_in_other == sum_in_other
    assert actual_size == size
    assert actual_pct_in_other == pct_in_other


@pytest.mark.parametrize("columns, left_keys, right_keys, expected_final_columns", [
    (["int_key", "str1"], ["int_key"], ["int_key"], ["int_key", "str1"]),
    (["int_key", "mult_int_key", "float1"], ["int_key"], ["mult_int_key"],
     ["int_key", "float1"])
])
def test_drop_other_key_columns(df_to_merge, columns, left_keys, right_keys,
                                expected_final_columns):
    # Given
    df = df_to_merge[columns]

    # When
    final_df = _drop_other_key_columns(df, left_keys, right_keys)

    # Then
    assert list(final_df.columns) == expected_final_columns
