import sys
from pathlib import Path
import pytest
from shutil import copytree
import pandas as pd
import numpy as np

TEST_FOLDER = Path(__file__).parent
sys.path.insert(0, str(TEST_FOLDER.parent))


@pytest.fixture(scope="session")
def data_folder():
    return TEST_FOLDER / "data"


@pytest.fixture()
def test_folder(tmp_path, data_folder):
    dst = tmp_path / "data"
    copytree(data_folder, dst)
    return dst


@pytest.fixture(scope="module")
def df_to_merge():
    df = pd.DataFrame({"float1": np.random.randn(20)})
    df["mult_int_key"] = list(range(10)) + list(range(10))
    df["int_key"] = range(20)
    df["mult_str_key"] = df["mult_int_key"].map(str)
    df["str_key"] = df["int_key"].map(str)
    df["str1"] = [chr(97 + i) for i in range(20)]
    df["int_key_with_nan"] = df["int_key"].map(lambda x: x if x % 2 else None)
    df["mult_col_int_key1"] = df["mult_col_int_key2"] = df["int_key"]
    df = df.rename(
        columns={"mult_col_int_key1": "mult_col_int_key", "mult_col_int_key2": "mult_col_int_key"})
    return df
