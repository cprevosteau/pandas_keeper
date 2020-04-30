"""Miscellaneous useful functions."""


def _cols(name, *other):
    if len(other):
        name = name if len(other) == 1 else _cols(name, *other[:-1])
        other_template = "%(other)s" if name == "" else name
        template = "%(name)s_%(other)s" if name != "" and other[-1] != "" else other_template
        return template % {"name": name, "other": other[-1]}
    else:
        return name


def make_cols(*names):
    """Return a generator of column names.

    The generator will produce column names starting by the concatenation of `*names`
    separated by '_'.
    Empty strings argument either for `make_cols` or for the returned generator will
    be ignored.

    Args:
        *names: Name(s) concatenated with '_' as separator to prefix column names.

    Examples:
        >>> make_cols("name")("sub_name")
        "name_subname"
        >>> make_cols("name1", "", "name_2")("", "sub_name_1", "sub_name_2")
        "name_1_name_2_sub_name_1_sub_name_2"
        >>> make_cols("")("sub_name")
        sub_name
        >>> make_cols("")("")
        ""

    """
    name = _cols("", *names) if len(names) else ""
    return lambda *x: _cols(name, *x)
