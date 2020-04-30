import json
import pickle as pk
import pandas as pd
from pandas_keeper import LOGGER


@LOGGER.timeit
def read(filename, *args, **kw):
    """Read the file whatever its extensions.

    Implemented extensions of file:
        - json
        - csv (or txt as a csv)
        - pickle (or pkl)
        - pq (parquet file)
        - sql (as a text file)
        - xls, xlsx or xlsm

    Args:
        filename (str): File path.
        *args: Variable length argument to pass to the underlying read function.
        **kw: Keyword arguments to pass to the underlying read function.
    """
    file_extension = filename.split(".")[-1]
    with open(filename) as f:
        if file_extension == "json":
            return json.load(f, *args, **kw)
        elif file_extension in ["csv", "txt"]:
            return pd.read_csv(f, *args, **kw)
        elif file_extension in ["pkl", "pickle"]:
            return pk.load(f, *args, **kw)
        elif file_extension in ["pq"]:
            return pd.read_parquet(f, *args, **kw)
        elif file_extension in ["sql"]:
            return f.read().decode()
        elif file_extension in ["xls", "xlsx", "xlsm"]:
            return pd.read_excel(f, *args, **kw)
        else:
            raise NotImplementedError("Read .%s files is not implemented." % file_extension)
