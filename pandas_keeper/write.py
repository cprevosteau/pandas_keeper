import os
import json
import pickle as pk
from pandas_keeper.logger import Logger

LOGGER = Logger()


@LOGGER.timeit
def write(obj, filename, *args, **kw):
    """Write the file whatever its extensions.

    Implemented extensions of file:
        - json
        - csv (or txt as a csv)
        - pickle (or pkl)
        - pq (parquet file)
        - sql (as a text file)

    Args:
        obj : Python object to write
        filename (str): File path.
        *args: Variable length argument to pass to the underlying write function.
        **kw: Keyword arguments to pass to the underlying write function.
    """
    file_extension = filename.split(".")[-1]
    try:
        with open(filename, "wb") as f:
            if file_extension == "json":
                json_file = json.dumps(obj, *args, **kw)
                f.write(str.encode(json_file))
            elif file_extension in ["csv", "txt"]:
                csv_file = obj.to_csv(*args, **kw)
                f.write(str.encode(csv_file))
            elif file_extension in ["pq"]:
                kw["engine"] = "pyarrow"
                obj.to_parquet(f, *args, **kw)
            elif file_extension in ["pkl", "pickle"]:
                pk.dump(obj, f, *args, **kw)
            elif file_extension == "sql":
                f.write(str.encode(obj))
            else:
                raise NotImplementedError("Write .%s files is not implemented." % file_extension)
    except Exception as e:  # If the writing has failed, remove the incompleted file
        try:
            os.remove(filename)
        except Exception as erase_error:
            print(erase_error)
        raise e
