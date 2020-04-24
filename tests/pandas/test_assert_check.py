import pandas as pd
import pytest
from tools.pandas.assert_check import replace_check, assert_column_values
# from tools.pandas.assert_check import assert_type


@pytest.mark.parametrize("df_dic, values, should_fail, case", [
    (
        {"str_range_10": list(map(str, range(10)))},
        [str(i) for i in range(10)],
        False,
        "list-like of good values"
    ), (
        {"str_range_10": list(map(str, range(10)))},
        {i: str(i) for i in range(10)},
        False,
        "dict of good values"
    ), (
        {"str_range_10_with_nan": list(map(str, range(7))) + [None, "8", None]},
        [str(i) for i in range(10)],
        False,
        "df with nan values"
    ), (
        {"str_range_10": list(map(str, range(10)))},
        [str(i) for i in range(8)],
        True,
        "8 and 9 are not in the allowed values."
    )
])
@pytest.helpers.assert_error
def test_assert_column_values(df_dic, values, case, should_fail):
    # Given
    df = pd.DataFrame(df_dic)

    # When
    assert_column_values(df, df.columns[0], values), case

    # Then depending on should_fail, it should fail


@pytest.fixture(scope="module")
def df():
    df = pd.DataFrame({
        "str_range_10": list(map(str, range(10))),
        "raise_error_str_range_10": list(map(str, range(10)))})

    df["str_range_10_with_nan"] = None
    df.loc[range(0, 10, 2), "str_range_10_with_nan"] = df.loc[range(0, 10, 2), "a"]

    df["int_range_10"] = df.a.astype(int)
    df["str_range_10_with_spaces"] = df["str_range_10"] + "  "
    df["str_range_10_with_nan_with_spaces"] = df["str_range_10_with_nan"] + "  "

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


@pytest.mark.parametrize("df_dic, values_dic, kw, should_fail, case", [
    (
            {
                "str_range_10": list(map(str, range(10))),
                "str_range_10_with_nan": list(map(str, range(7))) + [None, "8", None]},
            {
                "str_range_10": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan": {str(i): chr(97 + i) for i in range(15)}},
            {}, False, "normal case with one column with nan values should succeed"
    ),
    (
            {"str_range_10": list(map(str, range(10)))},
            {"str_range_10": {str(i): chr(97 + i) for i in range(9)}},
            {}, True, "Missing values to replace should fail"
    ), (
            {
                "str_range_10_with_spaces": list(map(lambda x: str(x) + "  ", range(10))),
                "str_range_10_with_nan_with_spaces": list(map(str, range(7))) + [
                    None, " 8 ", None]},
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": True}, False, "non strip values with strip option should succeed"
    ), (
            {
                "str_range_10_with_spaces": list(map(lambda x: str(x) + "  ", range(10))),
                "str_range_10_with_nan_with_spaces": list(map(str, range(7))) + [
                    None, " 8 ", None]},
            {
                "str_range_10_with_spaces": {str(i): chr(97 + i) for i in range(10)},
                "str_range_10_with_nan_with_spaces": {str(i): chr(97 + i) for i in range(10)}},
            {"strip": False}, True, "non strip values without strip option should fail"
    ), (
            {"a_j": list(map(lambda i: chr(97 + i), range(10))),
             "A_J": list(map(lambda i: chr(97 + i).upper(), range(10)))},
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": True}, False, "given uppercase values, it should succeed with lower options"
    ), (
            {"a_j": list(map(lambda i: chr(97 + i), range(10))),
             "A_J": list(map(lambda i: chr(97 + i).upper(), range(10)))},
            {"a_j": {chr(97 + i).upper(): i for i in range(10)},
             "A_J": {chr(97 + i): i for i in range(10)}},
            {"lower": False}, True, "given uppercase values, it should fail without lower options"
    )
])
@pytest.helpers.assert_error
def test_replace_check(df_dic, values_dic, kw, case, should_fail):
    df = pd.DataFrame(df_dic)
    replace_check(df, values_dic, **kw)
#
#
# @pytest.mark.parametrize("col, dtype, na_allowed, should_fail", [
#     ("a", "str", False, False),
#     ("a", "int", False, True),
#     ("a_with_nan", "str", True, False),
#     ("a_with_nan", "str", False, True),
#     ("a_with_spaces_with_num", "str", False, True),
#     ("a_with_spaces_with_num", "int", False, True)
# ])
# @pytest.mark.usefixtures("assert_error")
# def test_assert_type(df_to_remplace, col, dtype, na_allowed):
#     assert_type(df_to_remplace, col, dtype, na_allowed)
#
#
# @pytest.fixture(scope="module")
# def df_to_merge():
#     df = pd.DataFrame({"float1": np.random.randn(20)})
#     df["mult_int_key"] = list(range(10)) + list(range(10))
#     df["int_key"] = range(20)
#     df["mult_str_key"] = df["mult_int_key"].map(str)
#     df["str_key"] = df["int_key"].map(str)
#     df["str1"] = [chr(97 + i) for i in range(20)]
#     df["int_key_with_nan"] = df["int_key"].map(lambda x: x if x % 2 else None)
#     df["mult_col_int_key1"] = df["mult_col_int_key2"] = df["int_key"]
#     df = df.rename(
#        columns={"mult_col_int_key1": "mult_col_int_key", "mult_col_int_key2": "mult_col_int_key"})
#     return df
