from typing import Dict, Any, List
from pandas import DataFrame, Series
from .column_keeper import ColumnKeeper, check_df_keeper_columns_are_in_df
from .df_keeper import DFKeeper
from .read import read_data
from .. import safe_replace_series, assert_type

COLUMN_METHOD_NAMES = ["replace", "safe_replace"]
COLUMN_METHODS = {
    "safe_replace": safe_replace_series
}


def import_df(df_keeper_schema: Dict[str, Any]) -> DataFrame:
    df_keeper = DFKeeper(**df_keeper_schema)
    df = read_data(df_keeper.file_path, df_keeper.reader, **df_keeper.read_arguments)
    check_df(df, df_keeper.columns)
    if not df_keeper.keep_all_columns:
        df = df[[col.name for col in df_keeper.columns]]
    return df


def check_df(df: DataFrame, df_keeper_columns: List[ColumnKeeper]) -> None:
    check_df_keeper_columns_are_in_df(df, df_keeper_columns)
    for col in df_keeper_columns:
        if col.dtype is not None:
            assert_type(df[col], col.dtype, col.nullable)


def transform_column(pds: Series, column_keeper: ColumnKeeper) -> Series:
    for method_name in COLUMN_METHOD_NAMES:
        kwargs = getattr(column_keeper, method_name)
        kwargs["inplace"] = True
        if kwargs is not None:
            if method_name in COLUMN_METHODS:
                COLUMN_METHODS[method_name](pds, **kwargs)
            else:
                getattr(pds, method_name)(**kwargs)
    return Series
