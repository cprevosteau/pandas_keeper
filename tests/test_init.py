import pandas as pd
import pytest
from pandas_keeper import patch_pandas

DF_TO_MERGE = pytest.helpers.df_to_merge()
NEW_DF_METHODS = ["safe_merge", "safe_replace"]
NEW_SERIES_METHODS = ["assert_type", "assert_values", "safe_replace"]


def test_new_df_series_methods_become_it_only_after_pandas_tools_is_imported():
    # Given
    df_attributes = set(dir(DF_TO_MERGE))
    series_attributes = set(dir(DF_TO_MERGE["str_key"]))
    assert df_attributes - set(NEW_DF_METHODS) == df_attributes
    assert series_attributes - set(NEW_SERIES_METHODS) == series_attributes

    # When
    patch_pandas()
    new_df_attributes = set(dir(DF_TO_MERGE))
    new_series_attributes = set(dir(DF_TO_MERGE["str_key"]))

    # Then
    assert set(NEW_DF_METHODS) <= new_df_attributes
    assert set(NEW_SERIES_METHODS) <= new_series_attributes


def test_safe_replace_as_a_method_of_a_dataframe():
    # Given
    patch_pandas()
    df = DF_TO_MERGE[["str_key"]]
    replace_dic = {"str_key": {str(i): i for i in range(20)}}
    expected_df = pd.DataFrame({"str_key": range(20)})

    # When
    actual_df = df.safe_replace(replace_dic)

    # Then
    pd.testing.assert_frame_equal(actual_df, expected_df)


def test_safe_merge_as_a_method_of_a_dataframe():
    # Given
    patch_pandas()
    left_df = DF_TO_MERGE[["str_key"]]
    right_df = DF_TO_MERGE[["str_key", "int_key"]]

    # When
    merged_df = left_df.safe_merge(right_df, on="str_key")

    # Then
    pd.testing.assert_frame_equal(merged_df, right_df)


def test_assert_values_as_a_method_of_a_series():
    # Given
    patch_pandas()
    pds = DF_TO_MERGE["int_key"]

    # When/Then
    pds.assert_values(range(20))


def test_assert_type_as_a_method_of_a_series():
    # Given
    patch_pandas()
    pds = DF_TO_MERGE["int_key_with_nan"]

    # When/Then
    pds.assert_type("int", na_allowed=True)


def test_safe_replace_as_a_method_of_a_series():
    # Given
    patch_pandas()
    pds = pd.Series(range(10))
    expected_pds = pd.Series(str(i) for i in range(10))
    values = {i: str(i) for i in range(10)}

    # When
    actual_pds = pds.safe_replace(values)

    # Then
    pd.testing.assert_series_equal(actual_pds, expected_pds)
