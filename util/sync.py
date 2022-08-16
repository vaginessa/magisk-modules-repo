import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from modules import load_file_modules, write_file, load_file, load_url
from downloader import download_by_requests
from read_module import read_module_prop


class Sync:
    def __init__(self):
        self.root_folder = Path(__file__).resolve().parent
        self.repo_folder = self.root_folder.parent.joinpath("repo")
        self.modules_json = self.repo_folder.joinpath("modules.json")

        self.modules_mdict = load_file(self.modules_json)
        self.modules_mlist = load_file_modules(self.modules_json)

        self.status = 0

    def write_modules_json(self):
        self.modules_json = self.repo_folder.joinpath("modules.json")
        modules_json_bak = self.repo_folder.joinpath("modules.json.bak")

        print("moving old modules.json to modules.json.bak")
        shutil.move(self.modules_json, modules_json_bak)

        print("writing new modules.json")
        write_file(self.modules_mdict.dict, self.modules_json)

    @staticmethod
    def write_module_prop_json(file_dir: Path):
        _dict = read_module_prop(file_dir)

        print("writing module_prop.json")
        write_file(_dict, file_dir.parent.joinpath("module_prop.json"))

    @staticmethod
    def download_file(url, out):
        print("downloading {0}".format(out.name))
        download_by_requests(url, out)

    def pull(self, no_update_json=False):
        for item in self.modules_mlist:
            module_dir = self.repo_folder.joinpath(item.id)
            if not module_dir.exists():
                os.makedirs(module_dir)

            if "version" in item.status:
                file_dir = module_dir.joinpath("{0}-{1}.zip".format(item.id, item.status.version))
            else:
                file_dir = None

            if item.updateJson != "":
                update_json = load_url(item.updateJson)

                if int(update_json.versionCode) > int(item.status.versionCode):
                    self.status += 1
                    item["status"] = update_json.dict
                    self.modules_mdict["modules"] = self.modules_mlist.mdict2dict()

                    file_dir = module_dir.joinpath("{0}-{1}.zip".format(item.id, item.status.version))
                    self.download_file(item.status.zipUrl, file_dir)
                    self.write_module_prop_json(file_dir)
                else:
                    if not file_dir.exists():
                        self.download_file(item.status.zipUrl, file_dir)
                        self.write_module_prop_json(file_dir)
            else:
                if no_update_json:
                    self.download_file(item.status.zipUrl, file_dir)
                    self.write_module_prop_json(file_dir)

        if self.status > 0:
            self.write_modules_json()

    def push(self):
        if self.status > 0:
            msg = "timestamp: {0}".format(datetime.now())
            subprocess.run(['git', 'add', '.'], cwd=self.root_folder.parent)
            subprocess.run(['git', 'commit', '-m', msg], cwd=self.root_folder.parent)
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=self.root_folder.parent)


def main():
    sync = Sync()
    sync.pull(no_update_json=False)
    sync.push()


if __name__ == "__main__":
    main()
