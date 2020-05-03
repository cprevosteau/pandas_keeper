from pathlib import Path
import pytest
from pandas_keeper.df_keeper.column_keeper import ColumnKeeper
from pandas_keeper.df_keeper.df_keeper import DFKeeper
from pandas_keeper.df_keeper.read import DataReaderExtension


@pytest.mark.parametrize("schema, expected_df_keeper_dict", [
    ({"file_path": "data.csv"},
     {"file_path": Path("data.csv"), "reader": DataReaderExtension.csv}),
    ({"file_path": "data.csv", "reader": "parquet"},
     {"file_path": Path("data.csv"), "reader": DataReaderExtension.parquet}),
    ({"file_path": "data.csv", "read_arguments": {"sep": ";"}},
     {"file_path": Path("data.csv"), "reader": DataReaderExtension.csv,
      "read_arguments": {"sep": ";"}}),
    ({"file_path": "data.csv", "columns": [{"name": "Column 1"}, {"name": "Column 2"}]},
     {"file_path": Path("data.csv"), "reader": DataReaderExtension.csv,
      "columns": [ColumnKeeper(name="Column 1"), ColumnKeeper(name="Column 2")]}),
])
def test_df_keeper(schema, expected_df_keeper_dict):
    # Given
    expected_df_keeper = DFKeeper.construct(**expected_df_keeper_dict)

    # When
    df_keeper = DFKeeper(**schema)

    # Then
    assert df_keeper == expected_df_keeper
