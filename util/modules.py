import json
import requests
from pathlib import Path


class MDict:
    def __init__(self, _dict: dict = None):
        self._dict = dict()

        self.dict = _dict

    def __str__(self):
        return self._dict.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self._dict.get(item)

    def __setitem__(self, key, value):
        self._dict[key] = value
        if type(value) is dict:
            setattr(self, key, MDict(value))
        else:
            setattr(self, key, value)

    def __contains__(self, item):
        if item in self._dict:
            return True
        else:
            return False

    @property
    def dict(self):
        return self._dict

    @dict.setter
    def dict(self, _dict):
        self._dict = _dict
        for key in _dict.keys():
            item = _dict.get(key)

            if type(item) is dict:
                setattr(self, key, MDict(item))
            else:
                setattr(self, key, item)

    def get(self, key):
        return self._dict.get(key)


class MList(list):
    def __init__(self, _list: list = None, mdict=True):
        list.__init__([])
        if _list is None:
            self.extend([])
        else:
            if mdict:
                _list = self.dict2mdict(_list)
            self.extend(_list)

    def dict2mdict(self, _list=None):
        if _list is None:
            _list = self
        _list = [MDict(item) if type(item) is dict else item for item in _list]
        return _list

    def mdict2dict(self, _list=None):
        if _list is None:
            _list = self
        _list = [item.dict if type(item) is MDict else item for item in _list]
        return _list


def load_file(json_file: Path):
    json_dict = MDict(json.load(open(json_file, encoding="utf-8")))
    return json_dict


def write_file(json_dict: dict, json_file: Path):
    with open(json_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


def load_file_modules(json_file: Path):
    modules_list = MList(load_file(json_file).get("modules"))
    return modules_list


def load_url(url: str):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        block_size = 1024
        for data in response.iter_content(block_size):
            json_dict = MDict(json.loads(data))
            return json_dict
