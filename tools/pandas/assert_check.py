def assert_column_values(df, col, dic_or_values):
    """Assert that the column has values among expected ones.

    Args:
        df (DataFrame): DataFrame having the column to be checked.
        col (str): column name of the column to be checked.
        dic_or_values (set, list-like or dict): Values , or dictionary whose values, are
                                          allowed to be found in the column. N/A values
                                          are ignored.

    """
    values = dic_or_values if not isinstance(dic_or_values, dict) else dic_or_values.values()
    nn_col = df[col][df[col].notnull()]
    nn_col_in = nn_col.isin(values)
    assert nn_col_in.min() == 1, (
            "These values should not be present in the column %s: %s" %
            (col, list(nn_col[~nn_col_in].unique()))
    )


def replace_check(df, values, strip=True, lower=False):
    """Replace values in the dataframe and check that values are among the expected ones.

    Args:
        df (DataFrame): DataFrame having columns values to be replaced.
        values (dict of str, dict): Dictionary which for each key column name has a replacement
            dictionary of the form old_value -> new value. Once the replacement has taken place,
            the values of the resulting column is expecting to take values only in the new values of
            the replacement dictionary.
        strip (bool, default: True): Should the string values be stripped before replacing values ?
        lower (bool, default: False): Should the string values be lowered before replacing values ?
    """
    for col, dic in values.items():
        if strip and df.dtypes[col] == "object":
            str_idx = df[col].map(lambda x: isinstance(x, str))
            df.loc[str_idx, col] = df.loc[str_idx, col].str.strip()
        if lower and df.dtypes[col] == "object":
            str_idx = df[col].map(lambda x: isinstance(x, str))
            df.loc[str_idx, col] = df.loc[str_idx, col].str.lower()
            dic = {k.lower(): v for k, v in dic.items()}
        df[col] = df[col].replace(dic)
        assert_column_values(df, col, dic)
    return df


def assert_type(df, col, dtype, na_allowed):
    """Assert that the column has values of the expected type.

    Args:
        df (DataFrame): DataFrame having the column to be checked.
        col (str): column name of the column to be checked.
        dtype (dtype): Type expected to be found in the column values.
        na_allowed (bool): Are N/A values allowed ?

    """
    nn_idx = df[col].notnull()
    if not na_allowed:
        assert nn_idx.min() == 1, "The columns %s has null values." % col
    nn_col = df[col][nn_idx]
    wrong_values = set(nn_col[nn_col != nn_col.astype(dtype)])
    assert len(wrong_values) == 0, (
            "The column %s has value(s) of a type different from %s: %s" %
            (col, dtype, list(wrong_values))
    )
