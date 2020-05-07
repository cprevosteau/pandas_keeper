from pathlib import Path
import pandas as pd
from pandas import DataFrame
from enum import Enum
from pandas_keeper.logger import Logger
from typing import Dict, Callable

LOGGER = Logger()


class DataReaderExtension(Enum):
    csv = "csv"
    txt = "txt"
    pq = "pq"
    parquet = "parquet"
    json = "json"
    xls = "xls"
    xlsx = "xlsx"
    xlsm = "xlsm"


DATA_READER: Dict[DataReaderExtension, Callable[..., DataFrame]] = {
    DataReaderExtension.csv: pd.read_csv,
    DataReaderExtension.txt: pd.read_csv,
    DataReaderExtension.pq: pd.read_parquet,
    DataReaderExtension.parquet: pd.read_parquet,
    DataReaderExtension.json: pd.read_json,
    DataReaderExtension.xls: pd.read_excel,
    DataReaderExtension.xlsx: pd.read_excel,
    DataReaderExtension.xlsm: pd.read_excel
}


@LOGGER.timeit
def read_data(file_path: Path, file_reader_extension: DataReaderExtension,
              *args, **kw) -> DataFrame:
    return DATA_READER[file_reader_extension](file_path, *args, **kw)
