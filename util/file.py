import json
import requests
from pathlib import Path
from zipfile import ZipFile


class _Base:
    def __init__(self):
        self._dict = {}

    @property
    def dict(self):
        return self._dict


class _LoadJson(_Base):
    def __init__(self, json_file: Path):
        super().__init__()
        self._dict = json.load(open(json_file, encoding="utf-8"))


class _LoadJsonUrl(_Base):
    def __init__(self, url: str):
        super().__init__()
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            block_size = 1024
            for data in response.iter_content(block_size):
                self._dict = json.loads(data)


class _GetProps(_Base):
    def __init__(self, file: Path):
        super().__init__()
        z = ZipFile(file, "r")
        _props = z.read("module.prop")
        _props = _props.decode("utf-8")
        _list = _props.split('\n')

        for item in _list:
            prop = item.split('=')
            if len(prop) != 2:
                continue
            key, value = prop

            if key == "" or key.startswith("#"):
                continue

            self._dict[key] = value


load_json = _LoadJson
load_json_url = _LoadJsonUrl
get_props = _GetProps


def write_json(json_dict: dict, json_file: Path):
    with open(json_file, 'w') as f:
        json.dump(json_dict, f, indent=2)


def download_by_requests(url: str, out: Path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        block_size = 1024
        with open(out, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
