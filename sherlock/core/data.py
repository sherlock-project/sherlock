import json
import yaml

from sherlock.exception.slexception import SLException
from sherlock.exception.slunsupportedtypeexception import SLUnsupportedTypeException


class Data:
    def __init__(self, data):
        """
        Initialise the Data object with data.

        Parameters
        ----------
        data : dict
            The data loaded into the Data Object.
        """
        self._data = data
        self._data_keys = self._data.keys()

    @staticmethod
    def fromFile(filename, t="json"):
        """
        Creates a Data object from a file.

        Parameters
        ----------
        filename : str
            The file, which you would like to load from.

        t : str, optional, default = "json"
            The file time of which you're loading.  Supported formats are "json" and "yaml".

        """
        if t == "json":
            with open(filename, "r") as f:
                d = json.loads(f.read())
                f.close()
            return Data(data=d)
        if t == "yaml":
            with open(filename, "r") as f:
                d = yaml.loads(f.read())
                f.close()
            return Data(data=d)

        raise SLUnsupportedTypeException("Unsupported type '%s'" % t)

    def keys(self):
        """
        Gets the keys within the directory

        Parameters
        ----------
        return : list
            A list of keys are return.
        """
        return list(self._data_keys)

    def __len__(self):
        return len(self._data_keys)

    def __getitem__(self, i):
        d = self._data[i]
        return d

    def byindex(self, i: int):
        """

        Gets an entry by index instead of key.

        Parameters
        ----------
        i : int
            returns a tuple of key and data associated with the index i.
        """
        if len(self._data_keys) > i:
            key = self._data_keys[i]
            return (key, self._data[key])

        raise SLException("Out of index %i >= %i" % (i, len(self._data_keys)))
