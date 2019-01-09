import json


class SherlockData:
    def __init__(self, name="example", data={}):
        self._data = data
        self._name = name
        self._data_keys = self._data.keys()

    @staticmethod
    def fromFile(filename, t="json"):

        if t == "json":
            f = open(filename, "r")
            d = json.loads(f.read())
            f.close()
            return SherlockData(data=d)
        return SherlockData(data={})

    def keys(self):
        return self._data_keys

    def __len__(self):
        return len(self._data_keys)

    def __getitem__(self, i):
        d = self._data[i]
        return d

    def byindex(self, i):
        if len(self._data_keys) > i:
            key = self._data_keys[i]
            return (key, self._data[key])
