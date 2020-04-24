from collections import OrderedDict
import pytest
from pytest_lazyfixture import lazy_fixture
import pandas as pd
import numpy as np
import time
from tools.logger import Stringer, Logger


@pytest.fixture(scope="module")
def list_8():
    return list(range(8))


@pytest.fixture(scope="module")
def tuple_11():
    return tuple(range(11))


@pytest.fixture(scope="module")
def dict_6():
    return {x: 2 * x for x in range(6)}


@pytest.fixture(scope="module")
def df_6_9():
    return pd.DataFrame(np.random.rand(6, 9))


@pytest.fixture(scope="module")
def arr_10_3():
    return np.random.rand(10, 3)


@pytest.fixture(scope="module")
def stringer():
    return Stringer(display_floor_list_or_tuple=10, display_floor_dict=6)


class TestStringer(object):

    @pytest.mark.parametrize("stringer_args, list_or_tuple, expected_str", [
        ({"display_floor_list_or_tuple": 10}, lazy_fixture("list_8"),
         "(list(8): [0, 1, 2, 3, 4, 5, 6, 7])"),
        ({"display_floor_list_or_tuple": 10}, lazy_fixture("tuple_11"),
         "(tuple(11): (0, 1, 2, 3, 4, ... , 6, 7, 8, 9, 10))"),
        ({"display_floor_list_or_tuple": 11}, lazy_fixture("tuple_11"),
         "(tuple(11): (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10))")
    ])
    def test_list_or_tuple(self, stringer_args, list_or_tuple, expected_str):
        # Given
        stringer = Stringer(**stringer_args)

        # When
        actual_str = stringer.list_or_tuple(list_or_tuple)

        # Then
        assert actual_str == expected_str

    @pytest.mark.parametrize("stringer_args, expected_str", [
        ({"display_floor_dict": 6}, "(dict(6): {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10})"),
        ({"display_floor_dict": 5}, "(dict(6): {0: 0, 1: 2, ... , 4: 8, 5: 10})")
    ])
    def test_dict(self, stringer_args, expected_str, dict_6):
        # Given
        stringer = Stringer(**stringer_args)

        # When
        actual_str = stringer.dict(dict_6)

        # Then
        assert actual_str == expected_str

    def test_dataframe(self, stringer, df_6_9):
        # Given
        expected_str = "DataFrame(6, 9)"

        # When
        actual_str = stringer.dataframe(df_6_9)

        # Then
        assert actual_str == expected_str

    def test_numpy(self, stringer, arr_10_3):
        # Given
        expected_str = "numpy_array(10, 3)"

        # When
        actual_str = stringer.numpy(arr_10_3)

        # Then
        assert actual_str == expected_str

    @pytest.mark.parametrize("argument, expected_str, is_stringer_method", [
        (6, "6", False),
        (1.3, "1.3", False),
        (lazy_fixture("list_8"), "list_or_tuple", True),
        (lazy_fixture("tuple_11"), "list_or_tuple", True),
        (lazy_fixture("dict_6"), "dict", True),
        (lazy_fixture("df_6_9"), "dataframe", True),
        (lazy_fixture("arr_10_3"), "numpy", True),
        (range(1), "range", False)
    ])
    def test_argument(self, stringer, argument, expected_str, is_stringer_method):
        # Given
        expected_str = getattr(stringer, expected_str)(argument) if is_stringer_method \
            else expected_str

        # When
        actual_str = stringer.argument(argument)

        # Then
        assert actual_str == expected_str


class TestLogger(object):

    @pytest.fixture
    def log_file(self, tmpdir_factory):
        return tmpdir_factory.mktemp("logs").join("test.log")

    @pytest.fixture
    def logger(self, log_file):
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

    @pytest.fixture
    def arg_dic(self):
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

    @pytest.fixture
    def trivial_func(self):
        def func(a, b, c=3, *args, **kw):
            time.sleep(1)
            return 2

        return func

    @pytest.fixture
    def args_1(self, list_8):
        return range(3), "b", 3.5, 7, list_8

    @pytest.fixture
    def expected_dict_1(self, list_8, arg_dic):
        return OrderedDict([
            ("a", range(3)),
            ("b", "b"),
            ("c", 3.5),
            ("args", (7, list_8)),
            ("kw", arg_dic)
        ])

    @pytest.mark.parametrize("args, kwargs, expected_dict", [
        ((1, 2), {}, OrderedDict([("a", 1), ("b", 2), ("c", 3)])),
        (lazy_fixture("args_1"), lazy_fixture("arg_dic"), lazy_fixture("expected_dict_1"))
    ])
    def test_assign_arguments(self, logger, trivial_func, args, kwargs, expected_dict):
        # When
        actual_dic = logger.assign_arguments(trivial_func, *args, **kwargs)

        # Then
        assert actual_dic == expected_dict

    def test_start_str(self, logger, trivial_func, arg_dic):
        # Given
        len_provided_arguments = 4  # a, b, c=3 and **kw
        expected_fist_line_message = "test_logger.func started with arguments:"

        # When
        start_msg = logger.start_str(trivial_func, 1, 2, **arg_dic)

        # Then
        start_lines = start_msg.split("\n")
        assert start_lines[0] == expected_fist_line_message
        # first line with name of function plus one line per argument
        assert len(start_lines) == 1 + len_provided_arguments

    def test_timeit(self, logger, log_file, trivial_func, arg_dic):
        # Given
        logger.logger.setLevel("DEBUG")  # required to make logger worked in test environnement
        start_msg = logger.start_str(trivial_func, 1, 2, **arg_dic)
        decorated_func = logger.timeit(trivial_func)

        # When
        decorated_func(1, 2, **arg_dic)

        # Then
        log = log_file.read()
        log_lines = log.split("\n")
        # log = start_msg + timer + empty_new_line
        assert "func finished in 00:00:0" in log_lines[-2]
        assert len(log_lines) == len(start_msg.split("\n")) + 1 + 1
