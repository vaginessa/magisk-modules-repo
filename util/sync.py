import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from object import dict_, list_
from file import load_json, load_json_url, write_json, get_props, download_by_requests


class Sync:
    def __init__(self):
        self.root_folder = Path(__file__).resolve().parent
        self.repo_folder = self.root_folder.parent.joinpath("repo")
        self._file = self.repo_folder.joinpath("modules.json")

        self._dict = load_json(self._file).dict_
        self._list = list_(self._dict.modules).dict2dict_

    def write_modules_json(self):
        file_bak = self.repo_folder.joinpath("modules.json.bak")

        print("\nfile: moving old modules.json to modules.json.bak")
        shutil.move(self._file, file_bak)

        print("file: writing new modules.json")
        write_json(self._dict.dict, self._file)

    @staticmethod
    def download_file(url, out: Path):
        print("file: download {0}".format(out.name))
        download_by_requests(url, out)

    @staticmethod
    def move_file(file_dir: Path, version):
        file_name = "{0}-{1}.zip".format(file_dir.name.split('.')[0], version)
        print("file: move {0} to {1}".format(file_dir.name, file_name))
        shutil.move(file_dir, file_dir.parent.joinpath(file_name))

    @staticmethod
    def update_info(item: dict_, file_dir: Path):
        prop = get_props(file_dir).dict_
        item.name = prop.name
        item.version = prop.version
        item.versionCode = prop.versionCode
        item.author = prop.author
        item.description = prop.description

    def pull(self, download_all=True):
        for item in self._list:
            print("\nid: {0}".format(item.id))

            module_dir = self.repo_folder.joinpath(item.id)
            if not module_dir.exists():
                os.makedirs(module_dir)

            file_dir = module_dir.joinpath("{0}.zip".format(item.id))

            if item.updateJson != "":
                update_json = load_json_url(item.updateJson).dict_

                if "versionCode" in item:
                    if int(update_json.versionCode) > int(item.versionCode):
                        self.download_file(update_json.zipUrl, file_dir)
                        self.update_info(item, file_dir)
                        self.move_file(file_dir, item.version)

                        item.status = {
                            "zipUrl": update_json.zipUrl,
                            "changelog": update_json.changelog
                        }
                    else:
                        print("{0} already the latest version".format(item.id))

                elif not file_dir.exists():
                    self.download_file(update_json.zipUrl, file_dir)
                    self.update_info(item, file_dir)
                    self.move_file(file_dir, item.version)

                    item["status"] = {
                        "zipUrl": update_json.zipUrl,
                        "changelog": update_json.changelog
                    }

            else:
                print("{0} a no updateJson".format(item.id))
                if download_all:
                    self.download_file(item.status.get("zipUrl"), file_dir)
                    self.update_info(item, file_dir)
                    self.move_file(file_dir, item.version)

        self._dict.timestamp = str(datetime.now())
        self._dict.modules = self._list.dict_2dict
        self.write_modules_json()

    def push(self):
        msg = "timestamp: {0}".format(datetime.now())
        subprocess.run(['git', 'add', '.'], cwd=self.root_folder.parent)
        subprocess.run(['git', 'commit', '-m', msg], cwd=self.root_folder.parent)
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=self.root_folder.parent)


def main():
    sync = Sync()
    sync.pull(download_all=True)
    sync.push()


if __name__ == "__main__":
    main()
