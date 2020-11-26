from pathlib import Path
from typing import Dict, Any, List
from pydantic import root_validator
from pandas_keeper.df_keeper.model import Model
from pandas_keeper.df_keeper.column_keeper import ColumnKeeper
from pandas_keeper.df_keeper.read import DataReaderExtension


# noinspection PyMethodParameters
class DFKeeper(Model):

    file_path: Path
    reader: DataReaderExtension
    read_arguments: Dict[str, Any] = dict()
    columns: List[ColumnKeeper] = list()
    keep_undefined: bool = False

    @root_validator(pre=True)
    def set_reader(cls, values) -> Dict[str, Any]:
        reader = values.get("reader")
        if reader is None:
            reader = values["file_path"].split(".")[-1].lower()
        values["reader"] = DataReaderExtension(reader)
        return values
