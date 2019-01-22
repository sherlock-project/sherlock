import json,yaml


class Data:
    def __init__(self, name="example", data={}):
        self._data = data
        self._name = name
        self._data_keys = self._data.keys()

    @staticmethod
    def fromFile(filename, t="json"):
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
