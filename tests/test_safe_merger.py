import pytest
import pandas as pd
import numpy as np
from tools.pandas.safe_merger import assert_column_values, replace_check, assert_type, SafeMerger


class TestSafeMerger(object):

    @pytest.mark.parametrize("keys_dtypes, na_allowed, assert_error", [
        ({"int_key": "int", "str_key": "str"}, False, False),
        ({"int_key_with_nan": "int", "str_key": "str"}, True, False),
        ({"int_key_with_nan": "int"}, False, True),
        ({"int_key_with_nan": "int", "str_key": "str"}, False, True),
        (
                {"int_key_with_nan": "int", "str_key": "str"},
                {"int_key_with_nan": True, "str_key": False},
                False),
        ({"int_key_with_nan": "int", "str_key": "str"},
         {"int_key_with_nan": False, "str_key": False}, True),
        ({"non_present_column": "str"}, True, True),
        ({"mult_col_int_key": "int"}, False, True)
    ])
    @pytest.mark.usefixtures("assert_error")
    def test_init_and_check_key_columns(self, df_to_merge, keys_dtypes, na_allowed):
        SafeMerger(df_to_merge, keys_dtypes, na_allowed)

    @pytest.mark.parametrize(
        "left_columns, right_columns, keys_dtypes, on, left_on, right_on, left_keys, right_keys, "
        "assert_error",
        [
            (["int_key", "str1"], ["int_key", "float1"], {"int_key": "int"},
             None, None, None, ["int_key"], ["int_key"], False),
            (["int_key", "str1"], ["str_key", "float1"], {"int_key": "int"},
             None, None, None, None, None, True),
            (["int_key", "str_key"], ["int_key", "float1"], {"int_key": "int", "str_key": "str"},
             "int_key", None, None, ["int_key"], ["int_key"], False),
            (["int_key", "str_key"], ["int_key", "float1"], {"int_key": "int", "str_key": "str"},
             ["int_key"], None, None, ["int_key"], ["int_key"], False),
            (["int_key", "str_key"], ["int_key", "float1"], {"int_key": "int", "str_key": "str"},
             None, ["int_key"], "int_key", ["int_key"], ["int_key"], False),
            (["int_key", "str_key"], ["mult_col_int_key", "float1"],
             {"int_key": "int", "str_key": "str"},
             None, ["int_key"], "mult_col_int_key", ["int_key"], ["mult_col_int_key"], False),
            (["int_key", "str_key"], ["int_key", "float1"], {"int_key": "int", "str_key": "str"},
             None, None, "int_key", ["int_key"], ["int_key"], True),
            (["int_key", "str_key", "str1"], ["int_key", "str_key", "float1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key", "str_key"], None, None, ["int_key", "str_key"], ["int_key", "str_key"],
             False),
        ])
    @pytest.mark.usefixtures("assert_error")
    def test_check_get_right_left_keys(self, df_to_merge, left_columns, right_columns, keys_dtypes,
                                       on, left_on, right_on, left_keys, right_keys):
        sm = SafeMerger(df_to_merge[left_columns], keys_dtypes)
        l_keys, r_keys = sm._check_get_right_left_keys(df_to_merge[right_columns], on, left_on,
                                                       right_on)
        assert l_keys == left_keys
        assert r_keys == right_keys

    @pytest.mark.parametrize(
        "left_columns, right_columns, keys_dtypes, left_keys, right_keys, assert_error", [
            (["int_key", "str1"], ["int_key", "float1"], {"int_key": "int"},
             ["int_key"], ["int_key"], False),
            (["int_key", "float1"], ["int_key", "float1"], {"int_key": "int"},
             ["int_key"], ["int_key"], True),
            (["int_key", "float1", "str_key"], ["int_key", "str_key", "str1"], {"int_key": "int"},
             ["int_key"], ["int_key"], True),
            (["int_key", "float1", "str_key"], ["int_key", "str_key", "str1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key"], ["int_key"], True),
            (["int_key", "float1", "str_key"], ["int_key", "str_key", "str1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key", "str_key"], ["int_key", "str_key"], False)
        ])
    @pytest.mark.usefixtures("assert_error")
    def test_check_non_key_columns(self, df_to_merge, left_columns, right_columns, keys_dtypes,
                                   left_keys, right_keys):
        sm = SafeMerger(df_to_merge[left_columns], keys_dtypes)
        sm._check_non_key_columns(df_to_merge[right_columns], left_keys, right_keys)

    @pytest.mark.parametrize(
        "left_columns, right_columns, keys_dtypes, left_keys, right_keys, unique_right, assert_error",
        [
            (["int_key", "str1"], ["int_key", "float1"], {"int_key": "int"},
             ["int_key"], ["int_key"], True, False),
            (["int_key", "float1"], ["mult_int_key", "float1"], {"int_key": "int"},
             ["int_key"], ["mult_int_key"], True, True),
            (["int_key", "float1"], ["mult_int_key", "float1"], {"int_key": "int"},
             ["int_key"], ["mult_int_key"], False, False),
            (["int_key", "float1", "str_key"], ["int_key", "mult_str_key", "str1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key", "str_key"], ["int_key", "mult_str_key"], True, False),
            (["int_key", "float1", "str_key"], ["mult_int_key", "mult_str_key", "str1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key", "str_key"], ["mult_int_key", "mult_str_key"], True, True),
            (["int_key", "float1", "str_key"], ["mult_int_key", "mult_str_key", "str1"],
             {"int_key": "int", "str_key": "str"},
             ["int_key", "str_key"], ["mult_int_key", "mult_str_key"], False, False)
        ])
    @pytest.mark.usefixtures("assert_error")
    def test_check_unicity_and_matching_key_values(self, df_to_merge, left_columns, right_columns,
                                                   keys_dtypes,
                                                   left_keys, right_keys, unique_right):
        sm = SafeMerger(df_to_merge[left_columns], keys_dtypes)
        sm._check_unicity_and_matching_key_values(df_to_merge[right_columns], left_keys, right_keys,
                                                  unique_right)

    @pytest.mark.parametrize(
        "columns, keys_dtypes, left_keys, right_keys, right_cols_in_df, assert_error", [
            (["int_key", "str1"], {"int_key": "int"}, ["int_key"], ["int_key"], ["int_key"], False),
            (["int_key", "mult_int_key", "float1"], {"int_key": "int"}, ["int_key"],
             ["mult_int_key"], ["int_key"], False),
            (["int_key", "mult_int_key", "float1"], {"int_key": "int"}, ["int_key"],
             ["mult_int_key"], ["mult_int_key"], True),
        ])
    @pytest.mark.usefixtures("assert_error")
    def test_drop_right_key_columns(self, df_to_merge, columns, keys_dtypes, left_keys, right_keys,
                                    right_cols_in_df):
        sm = SafeMerger(df_to_merge[columns].copy(), keys_dtypes)
        sm._drop_right_key_columns(left_keys, right_keys)
        for col in right_cols_in_df:
            assert col in sm.df.columns
