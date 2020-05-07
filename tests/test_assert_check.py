import pandas as pd
import pytest
from pandas import DataFrame, Series
from pandas_keeper.assert_check import safe_replace, assert_values, assert_type, \
    safe_replace_series, assert_non_null_idx

DF = pd.DataFrame({
    "str_range_10": list(map(str, range(10))),
    "str_range_10_with_nan": [*map(str, range(7)), None, "8", None],
    "str_range_10_with_spaces": list(map(lambda x: str(x) + "  ", range(10))),
    "str_range_10_with_nan_with_spaces": [*map(str, range(7)), None, " 8 ", None],
    "str_and_int_10": [0, 1, 2, 3, 4, "5", 6, "7", "8", "9"],
    "a_j": list(map(lambda i: chr(97 + i), range(10))),
    "A_J": list(map(lambda i: chr(97 + i).upper(), range(10)))
})


@pytest.mark.parametrize("pds, values, should_fail, case", [
    (
            DF["str_range_10"],
            [str(i) for i in range(10)],
            False,
            "list-like of good values"
    ), (
            DF["str_range_10"],
            {str(i) for i in range(10)},
            False,
            "set of good values"
    ), (
            DF["str_range_10_with_nan"],
            [str(i) for i in range(10)],
            False,
            "df with nan values"
    ), (
            DF["str_range_10"],
            [str(i) for i in range(8)],
            True,
            "8 and 9 are not in the allowed values."
    )
])
@pytest.helpers.assert_error
def test_assert_values(pds: Series, values, should_fail, case):
    # When/Then depending on should_fail, it should fail
    assert_values(pds, values), case


@pytest.mark.parametrize("df, values_dic, kw, expected_df_dic, should_fail, case", [
    (
            DF[["str_range_10", "str_range_10_with_nan"]],
            {
                "str_range_10": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan": {str(i): chr(97 + i) for i in range(15)}},
            {"inplace": True}, {
                "str_range_10": [chr(97 + i) for i in range(10)],
                "str_range_10_with_nan": [*(chr(97 + i) for i in range(7)), None, chr(97 + 8), None]
            }, False, "normal case with one column with nan values should succeed"
    ),
    (
            DF[["str_range_10", "str_range_10_with_nan"]],
            {
                "str_range_10": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan": {str(i): chr(97 + i) for i in range(15)}},
            {"inplace": False}, {
                "str_range_10": [chr(97 + i) for i in range(10)],
                "str_range_10_with_nan": [*(chr(97 + i) for i in range(7)), None, chr(97 + 8), None]
            }, False, "normal case with one column with nan values should succeed"
    ),
    (
            DF[["str_range_10"]],
            {"str_range_10": {str(i): chr(97 + i) for i in range(9)}},
            {}, {}, True, "Missing values to replace should fail"
    ), (
            DF[["str_range_10_with_spaces", "str_range_10_with_nan_with_spaces"]],
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": True}, {
                "str_range_10_with_spaces": [chr(97 + i) for i in range(10)],
                "str_range_10_with_nan_with_spaces": [*(chr(97 + i) for i in range(7)), None,
                                                      chr(97 + 8), None]
            }, False, "non strip values with strip option should succeed"
    ), (
            DF[["str_range_10_with_spaces", "str_range_10_with_nan_with_spaces"]],
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": {"str_range_10_with_spaces": True,
                       "str_range_10_with_nan_with_spaces": False}},
            {}, True, "non strip values without strip option should fail"
    ), (
            DF[["a_j", "A_J"]],
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": True}, {
                "a_j": [i for i in range(10)],
                "A_J": [i for i in range(10)]},
            False, "given uppercase values, it should succeed with lower options"
    ), (
            DF[["a_j", "A_J"]],
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": {"a_j": True, "A_J": False}}, {}, True,
            "given uppercase values, it should fail without lower options"
    )
])
@pytest.helpers.assert_error
def test_safe_replace(df: DataFrame, values_dic, kw, expected_df_dic, should_fail, case):
    # Given
    df = df.copy()
    expected_df = pd.DataFrame(expected_df_dic)
    inplace = kw.get("inplace", False)

    # When
    replaced_df = safe_replace(df, values_dic, **kw)
    if inplace:
        actual_df = df
    else:
        actual_df = replaced_df

    # Then
    if not should_fail:
        pd.testing.assert_frame_equal(actual_df, expected_df)


@pytest.mark.parametrize("pds, values_dic, kw, expected_pds_list, should_fail, case", [
    (
        DF["str_range_10"], {str(i): chr(97 + i) for i in range(10)},
        {"inplace": True}, [chr(97 + i) for i in range(10)], False,
        "normal case with str values to int."
    ),
    (
        DF["str_range_10_with_nan"], {str(i): chr(97 + i) for i in range(15)},
        {"inplace": True}, [*(chr(97 + i) for i in range(7)), None, chr(97 + 8), None], False,
        "normal case with nan values should succeed."
    ),
    (
        DF["str_range_10"], {str(i): chr(97 + i) for i in range(9)},
        {}, {}, True, "Missing values to replace should fail"
    ), (
        DF["str_range_10_with_spaces"], {str(i): chr(97 + i) for i in range(10)},
        {"strip": True}, [chr(97 + i) for i in range(10)], False,
        "non strip values with strip option should succeed"
    ), (
        DF["str_range_10_with_nan_with_spaces"], {str(i): chr(97 + i) for i in range(10)},
        {"strip": True}, [*(chr(97 + i) for i in range(7)), None, chr(97 + 8), None], False,
        "non strip values with nan with strip option should succeed"
    ), (
        DF["str_range_10_with_spaces"], {str(i): chr(97 + i) for i in range(10)},
        {"strip": False}, [], True, "non strip values without strip option should fail"
    ), (
        DF["A_J"], {chr(97 + i): i for i in range(10)}, {"lower": True}, [i for i in range(10)],
        False, "given uppercase values, it should succeed with lower options"
    ), (
        DF["A_J"], {chr(97 + i): i for i in range(10)}, {"lower": False}, [i for i in range(10)],
        True, "given uppercase values, it should fail without lower option."
    )
])
@pytest.helpers.assert_error
def test_safe_replace_series(pds: Series, values_dic, kw, expected_pds_list, should_fail, case):
    pds = pds.copy()
    inplace = kw.get("inplace", False)
    expected_pds = None
    if not should_fail:
        expected_pds = pd.Series(expected_pds_list)
        expected_pds.name = pds.name

    # When
    replaced_pds = safe_replace_series(pds, values_dic, **kw)
    if inplace:
        actual_pds = pds
    else:
        actual_pds = replaced_pds

    # Then
    if not should_fail:
        pd.testing.assert_series_equal(actual_pds, expected_pds)


@pytest.mark.parametrize("pds, dtype, na_allowed, should_fail, case", [
    (DF["str_range_10"], "str", False, False,
     "given string values against string type, it should succeed"),
    (DF["str_range_10"], "int", False, True,
     "given string values against int type, it should fail"),
    (DF["str_range_10_with_nan"], "str", True, False,
     "given nan values with na allowed, it should succeed"),
    (DF["str_range_10_with_nan"], "str", False, True,
     "given nan values with na not allowed, it should fail"),
    (DF["str_and_int_10"], "str", False, True,
     "given int and string values against string type, it should fail"),
    (DF["str_and_int_10"], "int", False, True,
     "given int and string values against int type, it should fail"),
])
@pytest.helpers.assert_error
def test_assert_type(pds, dtype, na_allowed, should_fail, case):
    # When/Then it should fail depending on should_fail
    assert_type(pds, dtype, na_allowed)


@pytest.mark.parametrize("pds, na_allowed, return_value, expected_returned_value, should_fail, "
                         "case", [
    (pd.Series(["1", "2"]), False, False, None, False, "non null values, without returning values"),
    (pd.Series([2, 1]), False, True, pd.Series([True, True]), False,
     "non null values, returning values"),
    (pd.Series([2, 1, None, 3]), False, True, None, True, "should fail because of null values"),
    (pd.Series([2, 1, None, 3]), True, True, pd.Series([True, True, False, True]), False,
     "should return non null index")
])
@pytest.helpers.assert_error
def test_assert_non_null_idx(pds, na_allowed, return_value, expected_returned_value, should_fail,
                             case):
    # When
    actual_non_null_idx = assert_non_null_idx(pds, na_allowed, return_value)

    # Then
    if not should_fail:
        if expected_returned_value is not None:
            pd.testing.assert_series_equal(actual_non_null_idx, expected_returned_value)
        else:
            assert actual_non_null_idx is None
