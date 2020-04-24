import inspect
import logging
import numpy as np
import pandas as pd
import time
from functools import wraps


class Stringer(object):
    """Provide arguments representations depending on its type."""

    def __init__(self, display_floor_list_or_tuple=10, display_floor_dict=6):
        self.display_floor_list_or_tuple = display_floor_list_or_tuple
        self.display_floor_dict = display_floor_dict

    def list_or_tuple(self, l_or_t):
        """Generate the string representing a tuple or a list.

        Indicates the type object, the length and its contents of a tuple or a string.
        If the length exceeds `display_floor_list_or_tuple`, only the half of
        `display_floor_list_or_tuple` first elements and half of
        `display_floor_list_or_tuple` last elements are represented.
        Use print_arg for the representation of each element.

        Parameters
        ----------
        l_or_t: list or tuple,
            Object to be represented.

        Returns
        -------
        msg : string,
            Representation of the object

        """
        display_floor = self.display_floor_list_or_tuple
        if len(l_or_t) > display_floor:
            half_display = int(display_floor / 2)
            lt_body = [self.argument(x) for x in l_or_t[:half_display]]
            lt_body.append("... ")
            lt_body += [self.argument(x) for x in l_or_t[- half_display:]]
        else:
            lt_body = map(self.argument, l_or_t)
        if type(l_or_t) == list:
            lt_str = "[%s]" % ", ".join(lt_body)
        else:
            lt_str = "(%s)" % ", ".join(lt_body)
        msg = "(%s(%i): %s)" % (type(l_or_t).__name__, len(l_or_t), lt_str)
        return msg

    def dict(self, dic):
        """Generate the string representing the dictionary.

        Indicates the type object, the length and its contents of a tuple or a string.
        If the length exceeds `display_floor_list_or_tuple`, only the half of
        `display_floor_dict` first elements and half of
        `display_floor_dict` last elements are represented.
        Use print_arg for the representation of each element.

        Parameters
        ----------
        dic: dictionary,
            Object to be represented.

        Returns
        -------
        msg : string,
            Representation of the object

        """
        display_floor = self.display_floor_dict
        items = list(dic.items())
        if len(dic) > display_floor:
            half_display = int(display_floor / 2)
            dic_body = ["%s: %s" % (self.argument(k), self.argument(v))
                        for k, v in items[:half_display]]
            dic_body.append("... ")
            dic_body += ["%s: %s" % (self.argument(k), self.argument(v))
                         for k, v in items[- half_display:]]
        else:
            dic_body = ["%s: %s" % (self.argument(k), self.argument(v))
                        for k, v in items]
        dic_str = "{%s}" % ", ".join(dic_body)
        msg = "(dict(%i): %s)" % (len(dic), dic_str)
        return msg

    def DataFrame(self, df):
        """Generate the string representing the DataFrame.

        'Dataframe' and its shape are represented.

        Parameters
        ----------
        df: DataFrame,
            DataFrame to be represented.

        Returns
        -------
        msg : string,
            Representation of DataFrame

        """
        return "DataFrame%s" % (df.shape, )

    def numpy(self, arr):
        """Generate the string representing the DataFrame.

        'numpy_array' and its shape are represented.

        Parameters
        ----------
        arr: numpy.ndarray,
            Numpy array to be represented.

        Returns
        -------
        msg : string,
            Representation of numpy array

        """
        return "numpy_array%s" % (arr.shape, )

    def argument(self, arg):
        """Generate the string representing argument depending on its type.

        Parameters
        ----------
        arg: numpy.ndarray,
            Argument to be represented

        Returns
        -------
        msg : string,
            Representation of the argument

        """
        if type(arg) in [bool, int, float]:
            return str(arg)
        elif type(arg) == str:
            return "\"%s\"" % arg
        elif type(arg) in [list, tuple]:
            return self.list_or_tuple(arg)
        elif type(arg) == dict:
            return self.dict(arg)
        elif type(arg) == np.ndarray:
            return self.numpy(arg)
        elif type(arg) == pd.DataFrame:
            return self.DataFrame(arg)
        else:
            return str(type(arg).__name__)


class Logger(object):
    """Custom logger providing a timer of function.

    Attributes:
        logger (logging.Logger): Logger object
        stringer (Stringer): Stringer object

    "logging": {
        "logger_name": "PrepareData",
        "level": "DEBUG",
        "format": "%(asctime)s : %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "filename": "../logs/prepare_data.log",
        "filemode": "a",
        "use_console": true
    }

    """

    def __init__(self, logger_name=None, level=None, format=None, datefmt=None, filename=None,
                 filemode="a", use_console=True):
        # logging is by default using a console handler unless a filename is specified
        if use_console:
            logging.basicConfig(level=level, format=format, datefmt=datefmt)
        else:
            assert filename is not None, "filename must be specified when use_console=False"
            logging.basicConfig(level=level, format=format, datefmt=datefmt, filename=filename,
                                filemode=filemode)
        self.logger = logging.getLogger(logger_name)
        if use_console and filename is not None:
            # create console handler
            file_handler = logging.FileHandler(filename, filemode)
            if level is not None:
                file_handler.setLevel(level)

            # create formatter and add it to the handlers
            formatter = logging.Formatter(format,
                                          datefmt)
            file_handler.setFormatter(formatter)

            # add the handlers to logger
            self.logger.addHandler(file_handler)
        self.stringer = Stringer()

    @staticmethod
    def assign_arguments(func, *args, **kw):
        """Assign arguments with the argument name of the function.

        Parameters
        ----------
        func: function,
            Function used

        *args:
            Positional arguments passed to the function

        **kw:
            Keyword arguments passed to the function

        Returns
        -------
        args : dictionary,
            Key: argument name
            Value: value passed to the function

        """
        sig = inspect.signature(func)
        args = sig.bind(*args, **kw).arguments
        # add default values of the function
        for param in sig.parameters.values():
            if param.name not in args and param.default is not param.empty:
                args[param.name] = param.default
        return args

    def start_str(self, func, *args, **kw):
        """Generate the log message before the function excecution.

        Gives the parameters passed to the function.

        Parameters
        ----------
        func: function,
            Function to be executed

        *args:
            Positional arguments passed to the function

        **kw:
            Keyword arguments passed to the function

        Returns
        -------
        msg: string,
            Log message

        """
        arguments = self.assign_arguments(func, *args, **kw)
        fmt_str = "%s.%s started with arguments:\n    %s"
        res_dic = {}
        for k, v in arguments.items():
            res_dic[k] = self.stringer.argument(v)
        args_str = "\n    ".join(["%s: %s" % (k, v) for k, v in res_dic.items()])
        msg = fmt_str % (func.__module__, func.__name__, args_str)
        return msg

    def timeit(self, method):
        """Debug log arguments passed to the function and the execution time."""
        @wraps(method)
        def timed(*args, **kw):
            self.logger.debug(self.start_str(method, *args, **kw))
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            time_str = time.strftime('%H:%M:%S', time.gmtime(te - ts))
            self.logger.debug('%s.%s finished in %s' %
                              (method.__module__, method.__name__, time_str))
            return result
        return timed
