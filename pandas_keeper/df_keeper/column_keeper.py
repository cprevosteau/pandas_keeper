from typing import Callable, Dict, Any, Optional, List, Tuple
from pandas import Series, DataFrame
from pandas._typing import Dtype
from pydantic import root_validator
from pydantic.main import BaseModel
from pandas_keeper import safe_replace_series
from enum import Enum

from pandas_keeper.assert_check import _assert_empty_wrong_values


class ColumnActionName(Enum):
    safe_replace = "safe_replace"
    replace = "replace"
    fillna = "fillna"


# noinspection PyMethodParameters
class ColumnAction(BaseModel):  # type: ignore
    name: ColumnActionName
    method: Callable[..., Series]
    args: Tuple[Any, ...] = tuple()
    kwargs: Dict[str, Any] = {}

    @root_validator(pre=True)
    def set_method(cls, values):
        values["name"] = ColumnActionName(values["name"])
        if values["name"] is ColumnActionName.safe_replace:
            values["method"] = safe_replace_series
        else:
            values["method"] = getattr(Series, values["name"].name)
        return values


class ColumnKeeper(BaseModel):
    name: str
    dtype: Optional[Dtype] = None
    nullable: bool = True
    rename: Optional[str] = None
    actions: List[ColumnAction] = []
    drop: bool = False

    class Config:
        arbitrary_types_allowed = True


def check_df_keeper_columns_are_in_df(df: DataFrame, column_keepers: List[ColumnKeeper]) -> None:
    wrong_cols = set(map(lambda x: x.name, column_keepers)) - set(df.columns)
    _assert_empty_wrong_values(wrong_cols,
                               "Those columns are not in the DataFrame : %s" % wrong_cols)
