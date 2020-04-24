import inspect
import json
from tools.toolbox import TOOLBOX
from functools import wraps
import gc
import types
from copy import deepcopy
import os.path as osp


class Data(object):
    """Class reprensenting a Data object.

    Attributes:
        name (str): Name of the Data
        path (str, optional): Relative path in the data folder
        read_options (dict, optional) : Known arguments to pass to the read function to read the data
        write_options (dict, optional) : Known arguments to pass to the write function to wrtie the data
        overwrite (bool) : Should the data file be owertwritten if it already exists ?

    """

    def __init__(self, name, path=None, read_options={}, write_options={}, overwrite=False, copy=True, description=""):
        self.name = name
        self.path = path
        self.read_options = read_options
        self.write_options = write_options
        self.overwrite = overwrite
        self.copy = copy
        self.description = description
        self._data = None  # Loaded data if not None

    def get_data(self):
        """Return the data.

        If no data are loaded, try to read the file from its path
        and keep the data loaded.

        """
        if self._data is None:
            if self.path is not None:
                self._data = TOOLBOX.read(self.path, **self.read_options)
            else:
                raise FileNotFoundError("A path for the data %s must be specified." % self.name)
        if self.copy:
            return deepcopy(self._data)
        else:
            return self._data

    def unload(self):
        """Unload the data in memory."""
        self._data = None
        gc.collect()
        return self

    def set_data(self, data, to_write=False):
        """Assign data to the Data object.

        If `to_write=True`, the data is written.
        """
        self._data = data
        if to_write:
            self._write()
        gc.collect()
        return self

    def _write(self):
        assert self.path is not None, "A path must be specified"
        if self.overwrite or not TOOLBOX.exists(self.path):
            TOOLBOX.write(self._data, self.path, **self.write_options)

    @property
    def loaded(self):
        """Is the data loaded in memory ?"""
        return self._data is not None


class DataManager(object):
    """Class managing a collection of Data instances.

    Attributes:
        conf (dict): Data configuration from `conf/data.json`
        data (list of Data): Collection of Data instances shared by each member.

    """

    @staticmethod
    def _make_data(conf):
        """Charge les configurations de Data dans le DataManager sous forme de Data."""
        data = {}
        for name, attrs in conf["info"].items():
            data[name] = Data(name, **attrs)
            if conf.get("general_overwrite", None) is not None:
                data[name].overwrite = conf["general_overwrite"]
        return data

    with open(TOOLBOX.conf_dir("data.json")) as f:
        CONF = json.load(f)
    DATA = _make_data.__func__(CONF)

    def __init__(self, conf=None):
        if conf is None:
            self.conf = DataManager.CONF
            self.data = DataManager.DATA
        else:
            self.conf = conf
            self.data = DataManager._make_data(self.conf)

    def add_data(self, name, **kw):
        """Add a Data instance to the shared collection.

        Args:
            name (str): Name given at the Data instance
            kw (dict): Kwowns arguments to pass to the Data constructor.

        Return:
            The new Data instance.
        """
        self.data[name] = Data(name, **kw)
        return self.data[name]

    def unload_all_data(self):
        """Unload all the Data."""
        for data in self.data.values():
            data.unload()
        return self


class DataProcessor(DataManager):
    """Class for processing data to produce an output Data.

    Attributes:
        target (str): Name of the output Data either existing in `data` or being addd to `data`.
        to_write (bool, optional): Should the target be written ?
        from_data (bool, optional): Should the target be loaded from the DataManager if the target Data has already a content ?

    """

    def __init__(self, output=None, to_write=False, from_data=False, unload=None):
        super().__init__()
        if output is not None:
            if output in self.data:
                self.target = self.data[output]
            else:
                self.target = self.add_data(output)
        else:
            self.target = None
            assert not to_write and not from_data, "If target_name is None, to_write or from_data should not be True"
        self.to_write = to_write
        if self.to_write:
            assert self.target.path is not None, "to_write option cannot be True if no path for the output is specified."
        self.from_data = from_data
        if unload is not None:
            if not isinstance(unload, list):
                self.unload = [unload]
            else:
                self.unload = unload
        else:
            self.unload = []

    def run_load(self, func, *args, **kw):
        """Run function producing the target Data.

        If `to_write` set to True and the file already exists and its `overwrite` attribute is set to False,
        or if `from_data` is set to True and the target Data has a content,
        then it will return the file content or in memory content without executing the function.
        Otherwise, it runs the function and set the result as the data of the target Data.
        And then the data is written if `to_write`.
        """
        if self.to_write and not self.target.overwrite and TOOLBOX.exists(self.target.path):
            return self.target.get_data()
        elif self.from_data and self.target.loaded:
            return self.target.get_data()
        else:
            kw = self._inject_data(func, *args, **kw)
            data = func(*args, **kw)
            if self.target is not None:
                self.target.set_data(data, self.to_write)
            return data

    def _inject_data(self, func, *args, **kw):
        """Inject the data in the known arguments of the function.

        Return the known arguments of `func` updated with data from `data`
        having the same name than the missing arguments of the function.

        Args:
            func (function): Function requiring data as arguments
            args: Positional arguments of `func` already specified
            kw: Known arguments of `func` already specied
        """
        sig = inspect.signature(func)
        for arg in sig.parameters:
            # If arg is not already specified and is the name of a Data in `data`
            if arg not in sig.bind_partial(*args, **kw).arguments and arg in self.data:
                kw[arg] = self.data[arg].get_data()
        return kw

    def decorator(self, func):
        """See `DataProcessor.process`."""
        func = TOOLBOX.timeit(func)

        @wraps(func)
        def runner(*args, **kw):
            result = self.run_load(func, *args, **kw)
            for data in self.unload:
                self.data[data].unload()
            return result
        return runner

    @classmethod
    def process(cls, output=None, unload=None, to_write=False, from_data=False):
        """Decorate function requiring Data and resulting in an output Data.

        When the function is called, requiring data will be automatically inject
        in the arguments of the function based on the missing required argument's name and
        the Data name available in the `data` attribute shared in all DataManagement or DataProcessor instances.
        The result of the function will be stored as a Data instance in `data`.

        Args:
            ouput (str): Target Data name.
            unload (str or list of str, optional): Data name or list of Data name to unload once the function has been executed.
            to_write (bool, optional): Should the result data be written ?
            from_data (bool, optional): Should it return data in memory if it already exists ?

        Example:
            Example for a function computing recommandations from users and products data.
            We suppose here that users and products Data are in DataManager.data
            After executing the function, a Data name "recommandations" will be available and
            "products" and "users" Data contents will be unloaded from memory.

            >>> @DataProcessor.process(output="recommandations", unload=["users", "products"])
            ... def compute_recommandations(users, products):
            ...     ...
            ...     return recommandations_data

            >>> compute_recommandations()

        """
        processor = cls(output=output, to_write=to_write, from_data=from_data, unload=unload)
        return processor.decorator


class InstanceDataProcessor(object):
    """Decorator Class who wraps DataProcessor depending on the instance whom the method is decorated.

    Allow the use of arguments for DataProcessor depending of the attributes of the instance
    whom method is decorated at runtime via the use of alias of the form "_attr___" where "attr" is an
    instance string attribute. Thus at runtime, this alias will be replaced by the attribute value in the argument.
    This alias can also be used in the names of the arguments of the instance method, in order that the
    data are injected accordingly.

    Args:
        DataProcessor arguments

    Example:
        Example for a function computing purchasing score for users in a
        GiftVoucher class. We suppose here that `users` and `tir_groupe_liberte_characteristics`
        Data are in DataManager.data. After executing the function, a Data name
        "tir_groupe_liberter_score" will be available and `tir_groupe_liberte_characteristics`
        Data contents will be unloaded from memory.

        >>> class GiftVoucher(object):
        ...
        ...    def __init__(self, id):
        ...        self.id = id
        ...
        ...    @InstanceDataProcessor(output="_id____score", unload="_id____characteristics",
        ...                           attributes="id")
        ...    def compute_score(self, users, _id____characteristics):
        ...        ...
        ...        return score_data

        >>> GiftVoucher("tir_groupe_liberte").compute_score()
    """

    ALIAS = "_%s___"

    def __init__(self, output=None, unload=None, to_write=False, from_data=False):
        self.output = output
        self.unload = unload
        self.to_write = to_write
        self.from_data = from_data
        self.alias = InstanceDataProcessor.ALIAS

    def replace_attr(self, instance, arg):
        """Replace alias by attribute values."""
        if isinstance(arg, list):
            return list(map(lambda x: self.replace_attr(instance, x), arg))
        else:
            for attr in instance.__dict__:
                if type(arg) == str:
                    if self.alias % attr in arg:
                        arg = arg.replace(self.alias % attr, getattr(instance, attr))
            return arg

    def data_processor_factory(self, instance):
        """Generate DataProcessor.__init__ arguments depending on the instance."""
        kw = {}
        for arg in ["output", "unload", "from_data", "to_write"]:
            kw[arg] = self.replace_attr(instance, getattr(self, arg))
        return kw

    def patch_inject_data(self, dp, instance):
        """Replace the _inject_data method of DataProcessor to use alias accordingly."""
        def new_inject_data(dp_self, func, *args, **kw):
            sig = inspect.signature(func)
            for arg in sig.parameters:
                # If arg is not already specified and is the name of a Data in `data`
                if arg not in sig.bind_partial(*args, **kw).arguments:
                    new_arg = self.replace_attr(instance, arg)
                    if new_arg in dp_self.data:
                        kw[arg] = dp_self.data[new_arg].get_data()
            return kw
        dp._inject_data = types.MethodType(new_inject_data, dp)
        return dp

    def __call__(self, func):
        """Decorator."""
        @wraps(func)
        def decorated(instance, *args, **kw):
            dp = DataProcessor(**self.data_processor_factory(instance))
            dp = self.patch_inject_data(dp, instance)
            return dp.decorator(func)(instance, *args, **kw)
        return decorated


class ModelFolder(object):
    """Manage folders and files of a model.

    File tree for a model:
    ::

        /`models_folder`/
            `model_name`/
                `model_version`/
                    test/
                        x_train.pq
                        x_test.pq
                        y_train.pq
                        y_test.pq
                        report.json
                        model.pickle
                    prod/
                        x_train.pq
                        y_train.pq
                        model.pickle

    Args:
        model: model instance which should have a `name` attribute and a `version` attribute

    Attributes:
        name (str): model's name
        version (str): model's version
        model: model
        model_path (str): Path of the models folder
        test_path (str): Path of the test subfolder
        prod_path (str): Path of the production subfolder
        data (dict of Data): Collection of files to write as Data

    """

    def __init__(self, model):
        self.name = model.name
        self.version = model.version
        self.model = model
        self.model_path = TOOLBOX.conf["models_path"]
        self.test_path = osp.join(self.model_path, self.name, self.version, "test")
        self.prod_path = osp.join(self.model_path, self.name, self.version, "prod")
        self.data = self._make_data()

    def init_folders(self):
        """Create all the required folders."""
        if not TOOLBOX.exists(self.model_path):
            TOOLBOX.mkdir(self.model_path)
        if not TOOLBOX.exists(self.model_path, self.name):
            TOOLBOX.mkdir(self.model_path, self.name)
        if not TOOLBOX.exists(self.model_path, self.name, self.version):
            TOOLBOX.mkdir(self.model_path, self.name, self.version)

    def _make_data(self):
        """Create all the required files as Data in the DataManager."""
        data_conf = {}
        data_conf["test_x_train"] = {"path": osp.join(self.test_path, "x_train.pq")}
        data_conf["test_x_test"] = {"path": osp.join(self.test_path, "x_test.pq")}
        data_conf["test_y_train"] = {"path": osp.join(self.test_path, "y_train.pq")}
        data_conf["test_y_test"] = {"path": osp.join(self.test_path, "y_test.pq")}
        data_conf["test_model"] = {"path": osp.join(self.test_path, "model.pickle")}
        data_conf["test_report"] = {"path": osp.join(self.test_path, "report.json")}
        data_conf["prod_x_train"] = {"path": osp.join(self.prod_path, "x_train.pq")}
        data_conf["prod_y_train"] = {"path": osp.join(self.prod_path, "y_train.pq")}
        data_conf["prod_model"] = {"path": osp.join(self.prod_path, "model.pickle")}
        return DataManager._make_data({"info": data_conf})

    def set_test_data(self, X_train, X_test, y_train, y_test, report):
        """Set/Write all the data from the test folder."""
        self.init_folders()
        TOOLBOX.mkdir(self.test_path)
        self.data["test_x_train"].set_data(X_train, to_write=True)
        self.data["test_x_test"].set_data(X_test, to_write=True)
        self.data["test_y_train"].set_data(y_train, to_write=True)
        self.data["test_y_test"].set_data(y_test, to_write=True)
        self.data["test_report"].set_data(report, to_write=True)
        self.data["test_model"].set_data(self.model, to_write=True)

    def set_prod_data(self, X_train, y_train):
        """Set/Write all the data from the production folder."""
        TOOLBOX.mkdir(self.prod_path)
        self.data["prod_x_train"].set_data(X_train, to_write=True)
        self.data["prod_y_train"].set_data(y_train, to_write=True)
        self.data["prod_model"].set_data(self.model, to_write=True)
