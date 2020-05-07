from typing import Dict
from pandas import DataFrame
import pandas as pd
from pandas_keeper.df_keeper.read import DataReaderExtension, read_data
import pytest


@pytest.fixture(scope="session")
def df(data_folder):
    originial_file = data_folder / "data.csv"
    df = pd.read_csv(originial_file, sep=";")
    return df


WRITE_CONF: Dict[DataReaderExtension, Dict] = {
    DataReaderExtension.csv: {"method": DataFrame.to_csv, "kwargs": {"index": False}},
    DataReaderExtension.txt: {"method": DataFrame.to_csv, "kwargs": {"index": False}},
    DataReaderExtension.pq: {"method": DataFrame.to_parquet},
    DataReaderExtension.parquet: {"method": DataFrame.to_parquet},
    DataReaderExtension.json: {"method": DataFrame.to_json},
    DataReaderExtension.xls: {"method": DataFrame.to_excel, "kwargs": {"index": False}},
    DataReaderExtension.xlsx: {"method": DataFrame.to_excel, "kwargs": {"index": False}},
    DataReaderExtension.xlsm: {"method": DataFrame.to_excel, "kwargs": {"index": False,
                                                                        "engine": "openpyxl"}}
}


@pytest.mark.parametrize("extension, write",
                         [(extension, WRITE_CONF[extension]) for extension in DataReaderExtension])
def test_import_df(df, test_folder, extension, write):
    # Given
    path = test_folder / ("data.%s" % extension.value)
    write["method"](df, path, **write.get("kwargs", {}))
    # When
    read_df = read_data(path, extension)

    # Then
    pd.testing.assert_frame_equal(read_df, df)
