import pandas as pd
import pytest
from tools.pandas_tools import patch_pandas

DF_TO_MERGE = pytest.helpers.df_to_merge()


def test_safe_merge_is_not_an_attribute_of_df_if_pandas_tools_is_not_imported():
    assert "safe_merge" not in dir(DF_TO_MERGE)


def test_safe_merge_is_an_attribute_of_df_if_pandas_tools_is_imported():
    # When
    patch_pandas()

    # Then
    assert "safe_merge" in dir(DF_TO_MERGE)


def test_safe_merge_as_a_method_of_a_dataframe():
    # Given
    patch_pandas()
    left_df = DF_TO_MERGE[["str_key"]]
    right_df = DF_TO_MERGE[["str_key", "int_key"]]

    # When
    merged_df = left_df.safe_merge(right_df, on="str_key")

    # Then
    pd.testing.assert_frame_equal(merged_df, right_df)
