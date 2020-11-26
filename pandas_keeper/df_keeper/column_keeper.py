from collections.abc import Sequence
from typing import Callable, Dict, Any, Optional, List, Tuple
from pandas import Series, DataFrame
from pandas._typing import Dtype
from pydantic import validator
from pandas_keeper.df_keeper.model import Model
from pandas_keeper import safe_replace_series
from enum import Enum
from pandas_keeper.assert_check import _assert_empty_wrong_values, assert_type, assert_non_null_idx


class ColumnActionName(Enum):
    safe_replace = "safe_replace"
    replace = "replace"
    fillna = "fillna"
    astype = "astype"


INPLACE_ACTIONS = [ColumnActionName.safe_replace, ColumnActionName.replace, ColumnActionName.fillna]


# noinspection PyMethodParameters
class ColumnAction(Model):  # type: ignore
    name: ColumnActionName
    method: Callable[..., Optional[Series]] = None  # type: ignore
    args: Tuple[Any, ...] = tuple()
    kwargs: Dict[str, Any] = {}
    inplace: bool = False

    @validator("method", pre=True, always=True)
    def set_method(cls, _, values):
        if values["name"] is ColumnActionName.safe_replace:
            method = safe_replace_series
        else:
            method = getattr(Series, values["name"].name)
        return method

    @validator("inplace", always=True)
    def set_inplace(cls, _, values):
        return values["name"] in INPLACE_ACTIONS

    @validator("args", pre=True)
    def set_args(cls, args):
        if isinstance(args, str) or not isinstance(args, Sequence):
            args = (args, )
        return args

    @validator("kwargs", always=True)
    def set_inplace_or_copy_kwargs(cls, kwargs, values):
        if values["name"] == ColumnActionName.astype:
            kwargs["copy"] = False
        elif values["name"] in INPLACE_ACTIONS:
            kwargs["inplace"] = True
        return kwargs


class ColumnKeeper(Model):
    name: str
    dtype: Optional[Dtype] = None
    nullable: bool = False
    rename: Optional[str] = None
    actions: List[ColumnAction] = []
    drop: bool = False

    class Config:
        arbitrary_types_allowed = True


def check_df_keeper_columns_are_in_df(df: DataFrame, column_keepers: List[ColumnKeeper]) -> None:
    wrong_cols = set(map(lambda x: x.name, column_keepers)) - set(df.columns)
    _assert_empty_wrong_values(wrong_cols,
                               "Those columns are not in the DataFrame : %s" % wrong_cols)


def transform_column(pds: Series, action: ColumnAction) -> Series:
    if action.inplace:
        action.method(pds, *action.args, **action.kwargs)
    else:
        pds = action.method(pds, *action.args, **action.kwargs)
    return pds


def treat_column(pds: Series, column_keeper: ColumnKeeper) -> Series:
    for action in column_keeper.actions:
        pds = transform_column(pds, action)
    if column_keeper.dtype is not None:
        assert_type(pds, column_keeper.dtype, column_keeper.nullable)
    elif not column_keeper.nullable:
        assert_non_null_idx(pds, column_keeper.nullable)
    return pds
