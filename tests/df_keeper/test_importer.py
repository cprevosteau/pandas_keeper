from pandas_keeper.df_keeper.importer import import_df
import pandas as pd
import pytest


DATA_DF = pd.DataFrame({"Column 1": ["a", "b", "a", None], "Column 2": ["b", "c", "c", "d"]})


@pytest.mark.parametrize("schema, expected_df, should_fail, case", [
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}, "keep_all_columns": True},
     DATA_DF, False, "Just read a csv"),
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}, "keep_all_columns": False},
     DATA_DF[[]], False, "Read a csv but do not keep not specified columns."),
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}, "keep_all_columns": False,
      "columns": [{"name": "Column 2"}]},
     DATA_DF[["Column 2"]], False, "Read a csv but do not keep not specified columns.")
])
@pytest.helpers.assert_error
def test_import_df(test_folder, schema, expected_df, should_fail, case):
    # Given
    schema["file_path"] = str(test_folder / schema["file_path"])

    # When
    actual_df = import_df(schema)

    # Then
    if not should_fail:
        pd.testing.assert_frame_equal(actual_df, expected_df)
