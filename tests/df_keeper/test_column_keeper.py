import pytest
from pandas import Series
import pandas as pd
from pandas_keeper import safe_replace_series
from pandas_keeper.df_keeper.column_keeper import ColumnKeeper, ColumnActionName, ColumnAction, \
    check_df_keeper_columns_are_in_df, treat_column, transform_column

DF = pd.DataFrame({
    "str_range_10": list(map(str, range(10))),
    "str_range_10_with_nan": [*map(str, range(7)), None, "8", None],
    "str_range_10_with_spaces": list(map(lambda x: str(x) + "  ", range(10))),
    "str_range_10_with_nan_with_spaces": [*map(str, range(7)), None, " 8 ", None],
    "str_and_int_10": [0, 1, 2, 3, 4, "5", 6, "7", "8", "9"],
    "a_j": list(map(lambda i: chr(97 + i), range(10))),
    "A_J": list(map(lambda i: chr(97 + i).upper(), range(10)))
})


@pytest.mark.parametrize("schema, expected_column_keeper_dic, should_fail, case", [
    ({"name": "col1"}, {"name": "col1"}, False, "Test init just with name.")
])
@pytest.helpers.assert_error
def test_column_keeper(schema, expected_column_keeper_dic, should_fail, case):
    # Given
    expected_column_keeper = ColumnKeeper.construct(**expected_column_keeper_dic) \
        if not should_fail else None

    # When
    actual_column_keeper = ColumnKeeper(**schema)

    # Then
    if not should_fail:
        assert actual_column_keeper == expected_column_keeper


@pytest.mark.parametrize("schema, expected_column_action_dic", [
    ({"name": "safe_replace", "args": [{"a": "toto"}]},
     {"name": ColumnActionName.safe_replace, "method": safe_replace_series,
      "args": ({"a": "toto"}, ), "kwargs": {"inplace": True}, "inplace": True}),
    ({"name": "fillna", "args": "NaN"},
     {"name": ColumnActionName.fillna, "method": Series.fillna, "args": ("NaN", ),
      "kwargs": {"inplace": True}, "inplace": True}),
    ({"name": "replace", "kwargs": {"to_replace": {"10": 10}}},
     {"name": ColumnActionName.replace, "method": Series.replace, "kwargs":
         {"inplace": True, "to_replace": {"10": 10}}, "inplace": True}),
    ({"name": "replace", "args": {"10": 10}},
     {"name": ColumnActionName.replace, "method": Series.replace, "args": ({"10": 10},),
      "kwargs": {"inplace": True}, "inplace": True}),
    ({"name": "astype", "args": int},
     {"name": ColumnActionName.astype, "method": Series.astype, "args": (int, ),
      "kwargs": {"copy": False}, "inplace": False})
])
def test_column_action(schema, expected_column_action_dic):
    # Given
    expected_column_action = ColumnAction.construct(**expected_column_action_dic)

    # When
    actual_column_action = ColumnAction(**schema)

    # Then
    assert actual_column_action == expected_column_action


@pytest.mark.parametrize("df, df_keeper, should_fail, case", [
    (DF[["str_range_10", "a_j"]], [ColumnKeeper(name="str_range_10"), ColumnKeeper(name="a_j")],
     False, "all columns are well defined."),
    (DF[["str_range_10", "a_j"]], [ColumnKeeper(name="error"), ColumnKeeper(name="a_j")],
     True, "Wrong column name"),
])
@pytest.helpers.assert_error
def test_check_df_keeper_columns_are_in_df(df, df_keeper, should_fail, case):
    # When/Then it should fail depending on should_fail
    check_df_keeper_columns_are_in_df(df, df_keeper)


@pytest.mark.parametrize("pds, action, expected_pds", [
    (Series((str(i) for i in range(10))), ColumnAction(name="astype", args=["int64"]),
     Series(range(10))),
    (Series([*map(str, range(7)), None, "8", None]), ColumnAction(name="fillna", args="NA"),
     Series([*map(str, range(7)), "NA", "8", "NA"])),
    (Series(range(10)), ColumnAction(name="replace", args={9: "9"}),
     Series((*range(9), "9"))),
    (Series([*map(str, range(7)), None, "8", None]),
     ColumnAction(name="safe_replace", args={str(i): i for i in range(10)}),
     Series([*range(7), None, 8, None]))
])
def test_transform_column(pds, action, expected_pds):
    # When
    actual_pds = transform_column(pds, action)

    # Then
    pd.testing.assert_series_equal(actual_pds, expected_pds)


def test_treat_column():
    # Given
    col_name = "col1"
    pds = pd.Series(range(10), name=col_name)
    column_keeper = ColumnKeeper(name=col_name, dtype="int64", actions=[
        ColumnAction(name="safe_replace", args=[{i: str(i) for i in range(10)}]),
        ColumnAction(name="astype", args=[int])
    ], nullable=False)
    expected_pds = pd.Series((i for i in range(10)), name=col_name)

    # When
    actual_pds = treat_column(pds, column_keeper)

    # Then
    pd.testing.assert_series_equal(actual_pds, expected_pds)
