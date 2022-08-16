from pathlib import Path
from zipfile import ZipFile


def read_module_prop(file: Path):
    z = ZipFile(file, "r")
    info = z.read("module.prop")
    info = info.decode()
    info_list = info.split('\n')

    _dict = {}
    for item in info_list:
        if '=' in item:
            item = item.split('=')
            _dict[item[0]] = item[1]

    return _dict

