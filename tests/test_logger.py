import pytest
import pandas as pd
import numpy as np
import time
from tools.logger import Stringer, Logger
import logging


@pytest.fixture(scope="module")
def l8():
    return list(range(8))


@pytest.fixture(scope="module")
def t11():
    return tuple(range(11))


@pytest.fixture(scope="module")
def dic6():
    return{x: 2 * x for x in range(6)}


@pytest.fixture(scope="module")
def arg_dic():
    return {
            "int": 3,
            "float": 0.000000000000000001,
            "string": "string",
            "list<=10": list(range(9)),
            "list>10": list(range(100)),
            "dict<=10": {k: k ** 2 for k in range(8)},
            "dict>10": {k: k ** 2 for k in range(100)},
            "np_10x30": np.random.rand(10, 30),
            "df_100x1000": pd.DataFrame(np.random.rand(100, 1000)),
            "range": range(3)
        }


@pytest.fixture(scope="module")
def trivial_func():
    def func(a, b, c=3, *args, **kw):
        time.sleep(1)
        return 2
    return func


@pytest.fixture(scope="module")
def stringer():
    return Stringer(display_floor_list_or_tuple=10, display_floor_dict=6)


@pytest.fixture(scope="module")
def log_file(tmpdir_factory):
    return tmpdir_factory.mktemp("logs").join("test.log")


@pytest.fixture(scope="module")
def logger(log_file):
    log_conf = {
        "logger_name": "PrepareData",
        "level": "DEBUG",
        "format": "%(asctime)s : %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "filename": log_file,
        "filemode": "w",
        "use_console": True
    }
    return Logger(**log_conf)


class TestStringer(object):

    def test_list_or_tuple(self, l8, t11):
        stringer = Stringer(display_floor_list_or_tuple=10)
        assert stringer.list_or_tuple(l8) == "(list(8): [0, 1, 2, 3, 4, 5, 6, 7])"
        assert stringer.list_or_tuple(t11) == "(tuple(11): (0, 1, 2, 3, 4, ... , 6, 7, 8, 9, 10))"
        stringer.display_floor_list_or_tuple = 11
        assert stringer.list_or_tuple(t11) == "(tuple(11): (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10))"

    def test_dict(self, dic6):
        stringer = Stringer(display_floor_dict=6)
        assert stringer.dict(dic6) == "(dict(6): {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10})"
        stringer.display_floor_dict = 5
        assert stringer.dict(dic6) == "(dict(6): {0: 0, 1: 2, ... , 4: 8, 5: 10})"

    def test_DataFrame(self, stringer):
        df = pd.DataFrame(np.random.rand(6, 9))
        assert stringer.DataFrame(df) == "DataFrame(6, 9)"

    def test_numpy(self, stringer):
        arr = np.random.rand(10, 3)
        assert stringer.numpy(arr) == "numpy_array(10, 3)"

    def test_argument(self, stringer, l8, t11, dic6):
        assert stringer.argument(6) == "6"
        assert stringer.argument(1.3) == "1.3"
        assert stringer.argument("test") == "\"test\""
        assert stringer.argument(l8) == stringer.list_or_tuple(l8)
        assert stringer.argument(t11) == stringer.list_or_tuple(t11)
        assert stringer.argument(dic6) == stringer.dict(dic6)
        assert stringer.argument(range(1)) == "range"


class TestLogger(object):

    def test_assign_arguments(self, logger, trivial_func, arg_dic):
        logger.assign_arguments(trivial_func, 1, 2) == {"a": 1, "b": 2, "c": 3}
        exp_dic = {
            "a": range(3),
            "b": "b",
            "c": 3.5,
            "*args": (7, l8),
            "**kw": arg_dic
        }
        logger.assign_arguments(trivial_func, range(3), "b", 3.5, 7, l8, **arg_dic) == exp_dic

    def test_start_str(self, logger, trivial_func, arg_dic):
        start_msg = logger.start_str(trivial_func, 1, 2, **arg_dic)
        start_lines = start_msg.split("\n")
        len_provided_arguments = 4  # a, b, c and **kw
        assert len(start_lines) == 1 + len_provided_arguments  # first line with name of function plus one line per argument
        assert "func started with arguments:" in start_lines[0]

    def test_timeit(self, logger, log_file, trivial_func, arg_dic):
        logging.getLogger().setLevel("DEBUG")  # required to make logger worked in test environnement
        decorated_func = logger.timeit(trivial_func)
        decorated_func(1, 2, **arg_dic)
        log = log_file.read()
        log_lines = log.split("\n")
        start_msg = logger.start_str(trivial_func, 1, 2, **arg_dic)
        assert len(log_lines) == len(start_msg.split("\n")) + 1 + 1  # start_msg + timer + empty_new_line
        assert "func finished in 00:00:0" in log_lines[-2]
