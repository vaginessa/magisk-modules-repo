from pathlib import Path
from zipfile import ZipFile

from modules import MDict


def read_module_prop(file: Path):
    z = ZipFile(file, "r")
    info = z.read("module.prop")
    info = info.decode("utf-8")
    info_list = info.split('\n')

    info_dict = {}
    for item in info_list:
        if '=' in item:
            item = item.split('=')
            info_dict[item[0]] = item[1]

    return MDict(info_dict)
