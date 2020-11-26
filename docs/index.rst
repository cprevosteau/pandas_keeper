.. Pandas Keeper documentation master file, created by
    sphinx-quickstart on Thu Nov  5 17:57:56 2020.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to Pandas Keeper's documentation!
=========================================

Pandas Keeper is a overlay of Pandas which aims to make more dependable treatments done with Pandas

While treating data, assumptions are made upon them. If those assumptions become violated, the treatment is proned to errors and bugs whereas those violations arise often silently.
The goal of Pandas Keeper is make the data treatment reliable in writing down those assumptions, in order that none of those assumptions can be violated silently.

Getting Started
---------------

Imagine that you want import a dataset stored as a csv in `data.csv`, which has two columns `Column 1` and `Column 2`.
You know that Column 1 is a string column, et you want to rename this column `col_1`.
You will then declare these assumptions and transformations, and then import the dataset this way :

.. testsetup:: getting_started

    data_str = """Column 1,Column 2
    a,1
    b,2
    a,3
    ,4"""
    with open("data.csv", "w") as f:
       f.write(data_str)
    from pandas_keeper import import_df

.. testcleanup:: getting_started

   import os
   os.remove("data.csv")

.. doctest:: getting_started

    >>> with open("data.csv") as f:
    ...     print(f.read())
    Column 1,Column 2
    a,1
    b,2
    a,3
    ,4
    >>> from pandas_keeper import import_df
    >>> df_config = {
    ...    "file_path": "data.csv",
    ...    "columns": [
    ...        {
    ...            "name": "Column 1",
    ...            "dtype": str,
    ...            "nullable": True,
    ...            "rename": "col_1"
    ...        }
    ...    ]
    ... }
    >>> import_df(df_config)
      col_1
    0     a
    1     b
    2     a
    3   NaN

It returns then a pandas dataframe, which you can be sure is as described in the `df_config`.
Otherwise, it would have raised an error.
For example, if we declare a column not present in the data :

.. doctest:: getting_started

    >>> df_config = {
    ...    "file_path": "data.csv",
    ...    "columns": [
    ...        {
    ...            "name": "Col 2",
    ...        }
    ...    ]
    ... }
    >>> import_df(df_config)
    Traceback (most recent call last):
        ...
    AssertionError: Those columns are not in the DataFrame : {'Col 2'}

Or if we declare a wrong assumption:

.. doctest:: getting_started

    >>> df_config = {
    ...    "file_path": "data.csv",
    ...    "columns": [
    ...        {
    ...            "name": "Column 1",
    ...            "dtype": int,
    ...            "nullable": True
    ...        }
    ...    ]
    ... }
    >>> import_df(df_config)
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'a'

..
   Test

   .. toctree::
      :maxdepth: 2
      :caption: Contents:



   Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
