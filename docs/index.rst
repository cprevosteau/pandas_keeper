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

>>> from pandas_keeper import import_df
...
... df_config = {
...    "file_path": "data.csv",
...    "columns": [
...        {
...            "name": "Column 1",
...            "dtype": str,
...            "rename": "col_1"
...        }
...    ]
... }
...
... df = import_df(df_config)
>>> df.head()
  col_1  Column 2
0     a         1
1     b         2
2     a         3
3   NaN         4




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
