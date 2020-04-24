import pandas as pd
import pytest
from tools.pandas.assert_check import replace_check, assert_column_values, assert_type

DF = pd.DataFrame({
    "str_range_10": list(map(str, range(10))),
    "str_range_10_with_nan": list(map(str, range(7))) + [None, "8", None],
    "str_range_10_with_spaces": list(map(lambda x: str(x) + "  ", range(10))),
    "str_range_10_with_nan_with_spaces": list(map(str, range(7))) + [None, " 8 ", None],
    "str_and_int_10": [0, 1, 2, 3, 4, "5", 6, "7", "8", "9"],
    "a_j": list(map(lambda i: chr(97 + i), range(10))),
    "A_J": list(map(lambda i: chr(97 + i).upper(), range(10)))
})


@pytest.mark.parametrize("df, values, should_fail, case", [
    (
            DF[["str_range_10"]],
            [str(i) for i in range(10)],
            False,
            "list-like of good values"
    ), (
            DF[["str_range_10"]],
            {i: str(i) for i in range(10)},
            False,
            "dict of good values"
    ), (
            DF[["str_range_10_with_nan"]],
            [str(i) for i in range(10)],
            False,
            "df with nan values"
    ), (
            DF[["str_range_10"]],
            [str(i) for i in range(8)],
            True,
            "8 and 9 are not in the allowed values."
    )
])
@pytest.helpers.assert_error
def test_assert_column_values(df, values, case, should_fail):
    # Given
    df = pd.DataFrame(df)

    # When
    assert_column_values(df, df.columns[0], values), case

    # Then depending on should_fail, it should fail


@pytest.fixture(scope="module")
def df():
    df = pd.DataFrame({
        "str_range_10": list(map(str, range(10))),
        "raise_error_str_range_10": list(map(str, range(10)))})

    df["str_range_10_with_nan"] = None
    df.loc[range(0, 10, 2), "str_range_10_with_nan"] = df.loc[range(0, 10, 2), "str_range_10"]

    df["int_range_10"] = df.str_range_10.astype(int)
    df["str_range_10_with_spaces"] = " " + DF[["str_range_10"]] + "  "
    df["str_range_10_with_nan_with_spaces"] = " " + df["str_range_10_with_nan"] + "  "

    df["str_range_10_with_spaces_with_num"] = df["str_range_10_with_spaces"]
    idx = range(0, 10, 2)
    df.loc[idx, "str_range_10_with_spaces_with_num"] = df.loc[idx, "int_range_10"]

    df["a-j_raise_error_if_not_lower"] = list(map(lambda i: chr(97 + i), range(10)))
    return df


@pytest.fixture(scope="module")
def values(df_to_replace):
    replace_dic = {
        "a": {str(i): chr(97 + i) for i in range(10)},
        "raise_error_a": {str(i): chr(97 + i) for i in range(9)},
        "num_a": {i: chr(97 + i) for i in range(10)},
        "a_with_spaces_with_num": {i if i % 2 == 0 else str(i): chr(97 + i) for i in range(10)},
        "a_j_raise_error_if_not_lower": {chr(97 + i).upper(): i for i in range(10)}
    }
    replace_dic["raise_error_a"].update({9: chr(97 + 9)})
    replace_dic["a_with_nan"] = replace_dic["a_with_spaces"] = replace_dic[
        "a_with_nan_with_spaces"] = replace_dic["a"]
    assert len(set(replace_dic.keys()) - set(
        df_to_replace.columns)) == 0, "df_to_remplace columns and values keys must match."
    return replace_dic


@pytest.mark.parametrize("df, values_dic, kw, should_fail, case", [
    (
            DF[["str_range_10", "str_range_10_with_nan"]],
            {
                "str_range_10": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan": {str(i): chr(97 + i) for i in range(15)}},
            {}, False, "normal case with one column with nan values should succeed"
    ),
    (
            DF[["str_range_10"]],
            {"str_range_10": {str(i): chr(97 + i) for i in range(9)}},
            {}, True, "Missing values to replace should fail"
    ), (
            DF[["str_range_10_with_spaces", "str_range_10_with_nan_with_spaces"]],
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": True}, False, "non strip values with strip option should succeed"
    ), (
            DF[["str_range_10_with_spaces", "str_range_10_with_nan_with_spaces"]],
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": False}, True, "non strip values without strip option should fail"
    ), (
            DF[["a_j", "A_J"]],
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": True}, False, "given uppercase values, it should succeed with lower options"
    ), (
            DF[["a_j", "A_J"]],
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": False}, True, "given uppercase values, it should fail without lower options"
    )
])
@pytest.helpers.assert_error
def test_replace_check(df, values_dic, kw, case, should_fail):
    df = pd.DataFrame(df)
    replace_check(df, values_dic, **kw)


@pytest.mark.parametrize("df, dtype, na_allowed, should_fail, case", [
    (DF[["str_range_10"]], "str", False, False,
     "given string values against string type, it should succeed"),
    (DF[["str_range_10"]], "int", False, True,
     "given string values against int type, it should fail"),
    (DF[["str_range_10_with_nan"]], "str", True, False,
     "given nan values with na allowed, it should succeed"),
    (DF[["str_range_10_with_nan"]], "str", False, True,
     "given nan values with na not allowed, it should fail"),
    (DF[["str_and_int_10"]], "str", False, True,
     "given int and string values against string type, it should fail"),
    (DF[["str_and_int_10"]], "int", False, True,
     "given int and string values against int type, it should fail"),
])
@pytest.helpers.assert_error
def test_assert_type(df, dtype, na_allowed, should_fail, case):
    # Given
    col = df.columns[0]

    # When/Then it should fail depending on should_fail
    assert_type(df, col, dtype, na_allowed)
