import json

class SherlockData:
    def __init__(self, data={})
        self._data = {}
        self._data_keys = self._data.keys()
        
    def fromFile(self, 
        filename="", 
        type="json"):
        
        if type=="json":
            f = open(filename, "r")
            d = json.loads(f.read())
            f.close()
            return SherlockData(data=d)
        return SherlockData(data={})
        
    
    def __len__(self):
        return len(self._data_keys)
        
    def __getitem__(self, i):
        return  self._data[i]
        
    def byindex(self, i):
        if len(self._data_keys)>i:
            key = self._data_keys[i]
            return (key, self._data[key])
        
    
