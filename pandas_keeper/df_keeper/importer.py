from typing import Dict, Any
from pandas import DataFrame
from .column_keeper import check_df_keeper_columns_are_in_df, treat_column
from .df_keeper import DFKeeper
from .read import read_data


def import_df(df_keeper_schema: Dict[str, Any]) -> DataFrame:
    df_keeper = DFKeeper(**df_keeper_schema)
    df = read_data(df_keeper.file_path, df_keeper.reader, **df_keeper.read_arguments)
    check_df_keeper_columns_are_in_df(df, df_keeper.columns)
    if not df_keeper.keep_undefined:
        df = df[[col.name for col in df_keeper.columns]]
    for col in df_keeper.columns:
        df[col.name] = treat_column(df[col.name], col)
    to_drop = [col.name for col in df_keeper.columns if col.drop]
    df.drop(columns=to_drop, inplace=True)
    rename_values = {col.name: col.rename for col in df_keeper.columns if col.rename is not None}
    df.rename(columns=rename_values, inplace=True)
    return df
