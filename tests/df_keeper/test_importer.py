from pytest_helpers.utils import assert_error
from pandas_keeper.df_keeper.importer import import_df
import pandas as pd
import pytest


DATA_DF = pd.DataFrame({"Column 1": ["a", "b", "a", None], "Column 2": [1, 2, 3, 4]})


@pytest.mark.parametrize("schema, expected_df, should_fail, case", [
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}, "keep_undefined": True},
     DATA_DF, False, "Just read a csv"),
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}, "keep_undefined": False,
      "columns": [{"name": "Column 2"}]},
     DATA_DF[["Column 2"]], False, "Read a csv but keep only specified columns."),
    ({
         "file_path": "data.csv",
         "read_arguments": {"sep": ";"},
         "keep_undefined": False,
         "columns": [
             {
                 "name": "Error"
             },
             {
                 "name": "Column 2"
             }]},
     None, True, "Error in column name."),
    ({
             "file_path": "data.csv",
             "read_arguments": {"sep": ";"},
             "keep_undefined": False,
             "columns": [
                 {
                     "name": "Column 1",
                     "rename": "col_1",
                     "nullable": True
                 },
                 {
                     "name": "Column 2",
                     "drop": True
                 }
             ]
     },
     pd.DataFrame({"col_1": ["a", "b", "a", None]}), False, "Drop Column 2 and rename Column 1."),
    ({
         "file_path": "data.csv",
         "read_arguments": {"sep": ";"},
         "keep_undefined": True,
         "columns": [
             {
                 "name": "Column 1",
                 "actions": [{"name": "fillna", "args": "c"}],
                 "dtype": str,
                 "rename": "col_1"
             }
         ]
     },
     pd.DataFrame({"col_1": ["a", "b", "a", "c"], "Column 2": [1, 2, 3, 4]}), False,
     "treat column 1 but not column 2.")
])
@assert_error
def test_import_df(test_folder, schema, expected_df, should_fail, case):
    # Given
    schema["file_path"] = str(test_folder / schema["file_path"])

    # When
    actual_df = import_df(schema)

    # Then
    if not should_fail:
        pd.testing.assert_frame_equal(actual_df, expected_df)
