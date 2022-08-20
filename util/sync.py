import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from modules import write_file, load_file, load_url, MDict, MList
from downloader import download_by_requests
from read_module import read_module_prop


class Sync:
    def __init__(self):
        self.root_folder = Path(__file__).resolve().parent
        self.repo_folder = self.root_folder.parent.joinpath("repo")
        self.modules_json_file = self.repo_folder.joinpath("modules.json")

        self.modules_json_data: MDict = load_file(self.modules_json_file)
        self.modules_list: MList = self.modules_json_data.modules

    def write_modules_json(self):
        self.modules_json_file = self.repo_folder.joinpath("modules.json")
        modules_json_bak = self.repo_folder.joinpath("modules.json.bak")

        print("\nmoving old modules.json to modules.json.bak")
        shutil.move(self.modules_json_file, modules_json_bak)

        print("writing new modules.json")
        write_file(self.modules_json_data.dict, self.modules_json_file)

    @staticmethod
    def download_file(url, out: Path):
        print("downloading {0}".format(out.name))
        download_by_requests(url, out)

    @staticmethod
    def move_file(file_dir: Path, version):
        file_name = "{0}-{1}.zip".format(file_dir.name.split('.')[0], version)
        print("move {0} to {1}".format(file_dir.name, file_name))
        shutil.move(file_dir, file_dir.parent.joinpath(file_name))

    @staticmethod
    def update_info(item: MDict, file_dir: Path):
        prop = read_module_prop(file_dir)
        item["name"] = prop.name
        item["version"] = prop.version
        item["versionCode"] = prop.versionCode
        item["author"] = prop.author
        item["description"] = prop.description

    def pull(self, download_all=True):
        for item in self.modules_list:
            print("\nmodule id: {0}".format(item.id))

            module_dir = self.repo_folder.joinpath(item.id)
            if not module_dir.exists():
                os.makedirs(module_dir)

            file_dir = module_dir.joinpath("{0}.zip".format(item.id))

            if item.updateJson != "":
                update_json = load_url(item.updateJson)

                if "versionCode" in item:
                    if int(update_json.versionCode) > int(item.versionCode):
                        self.download_file(update_json.zipUrl, file_dir)
                        self.update_info(item, file_dir)
                        self.move_file(file_dir, item.version)

                        item["status"] = {
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
                    self.download_file(item.status.zipUrl, file_dir)
                    self.update_info(item, file_dir)
                    self.move_file(file_dir, item.version)

        self.modules_json_data["timestamp"] = str(datetime.now())
        self.modules_json_data["modules"] = self.modules_list.mdict2dict()
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
