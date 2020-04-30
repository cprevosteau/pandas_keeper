def assert_values(pds, values):
    """Assert that the column has values among expected ones.

    Args:
        pds (Series): Series to be checked.
        values (set, list-like): Values allowed to be found in the Series. N/A value are ignored.
    """
    nn_col = pds[pds.notnull()]
    nn_col_in = nn_col.isin(values)
    assert nn_col_in.min() == 1, (
            "These values should not be present in the pandas Series %s: %s" %
            (pds.name, list(nn_col[~nn_col_in].unique()))
    )


def safe_replace(df, values, strip=True, lower=False):
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
    for col, replace_dic in values.items():
        if strip and df.dtypes[col] == "object":
            str_idx = df[col].map(lambda x: isinstance(x, str))
            df.loc[str_idx, col] = df.loc[str_idx, col].str.strip()
        if lower and df.dtypes[col] == "object":
            str_idx = df[col].map(lambda x: isinstance(x, str))
            df.loc[str_idx, col] = df.loc[str_idx, col].str.lower()
            replace_dic = {k.lower(): v for k, v in replace_dic.items()}
        df[col] = df[col].replace(replace_dic)
        assert_values(df[col], replace_dic.values())
    return df


def assert_type(pds, dtype, na_allowed):
    """Assert that the column has values of the expected type.

    Args:
        pds (Series): Series to be checked.
        dtype (dtype): Type expected to be found in the column values.
        na_allowed (bool): Are N/A values allowed ?

    """
    nn_idx = pds.notnull()
    if not na_allowed:
        assert nn_idx.min() == 1, "The Series %s should not have null values." % pds.name
    nn_col = pds[nn_idx]
    wrong_values = set(nn_col[nn_col != nn_col.astype(dtype)])
    assert len(wrong_values) == 0, (
            "The Series %s has value(s) of a type different from %s: %s" %
            (pds.name, dtype, list(wrong_values))
    )
