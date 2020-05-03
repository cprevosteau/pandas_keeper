import pytest
from pandas import Series
from pandas_keeper import safe_replace_series
from pandas_keeper.df_keeper.column_keeper import ColumnKeeper, ColumnActionName, ColumnAction, \
    check_df_keeper_columns_are_in_df
from tests.test_assert_check import DF


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
      "args": ({"a": "toto"}, )}),
    ({"name": "fillna", "args": ["NaN"]},
     {"name": ColumnActionName.fillna, "method": Series.fillna, "args": ("NaN", )})
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
