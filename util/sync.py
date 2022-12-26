import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime

from file import load_json, load_json_url, write_json, get_props, download_by_requests
from progress import Progress

GITHUB_RAW_URL = "https://raw.githubusercontent.com"
MODULE_REPO = "ya0211/magisk-modules-repo"
REPO_BRANCH = "main"
REPO_URL = "{0}/{1}/{2}".format(GITHUB_RAW_URL, MODULE_REPO, REPO_BRANCH)


class Sync:
    def __init__(self, root_folder: Path):
        json_folder = root_folder.parent.joinpath("json")

        self.modules_folder = root_folder.parent.joinpath("modules")
        self.local_folder = root_folder.parent.joinpath("local")
        self.json_file = json_folder.joinpath("modules.json")
        self.json_dict = load_json(self.json_file).dict
        self.json_list = self.json_dict["modules"]

    def tmp_file(self, item: dict) -> Path:
        item_dir = self.modules_folder.joinpath(item["id"])
        if not item_dir.exists():
            os.makedirs(item_dir)

        return item_dir.joinpath("{0}.zip".format(item["id"]))

    def cloud_file(self, item: dict) -> Path:
        item_dir = self.modules_folder.joinpath(item["id"])
        return item_dir.joinpath("{0}.zip".format(item["version"].replace(" ", "_")))

    @staticmethod
    def update_file(url: str, file: Path):
        for f in sorted(glob("{0}/*".format(file.parent))):
            os.remove(f)
        download_by_requests(url, file)

    @staticmethod
    def update_info(item: dict, file: Path):
        prop = get_props(file).dict
        item["name"] = prop["name"]
        item["version"] = prop["version"]
        item["versionCode"] = prop["versionCode"]
        item["author"] = prop["author"]
        item["description"] = prop["description"]

    def upload_from_json(self, item: dict, update_json: dict):
        t_file = self.tmp_file(item)
        c_file = self.cloud_file(item)
        self.update_file(update_json["zipUrl"], t_file)
        self.update_info(item, t_file)
        shutil.move(t_file, c_file)

        item["states"] = {
            "zipUrl": "{0}/modules/{1}/{2}".format(REPO_URL, item["id"], c_file.name),
            "changelog": update_json["changelog"]
        }

    def upload_from_url(self, item: dict):
        t_file = self.tmp_file(item)
        c_file = self.cloud_file(item)
        self.update_file(item["update"], t_file)
        self.update_info(item, t_file)
        shutil.move(t_file, c_file)

        item["states"] = {
            "zipUrl": "{0}/modules/{1}/{2}".format(REPO_URL, item["id"], c_file.name),
            "changelog": ""
        }

    def upload_from_local(self, item: dict, file: Path):
        c_file = self.cloud_file(item)
        self.update_info(item, file)
        shutil.copy(file, c_file)

        item["states"] = {
            "zipUrl": "{0}/modules/{1}/{2}".format(REPO_URL, item["id"], c_file.name),
            "changelog": ""
        }

    def pull(self, update_all=True):
        pro = Progress(len(self.json_list), bar_length=60)
        for item in self.json_list:

            if item["update"].startswith("http"):
                if item["update"].endswith("json"):
                    update_json = load_json_url(item["update"]).dict
                    if "versionCode" in item:
                        c_file = self.cloud_file(item)
                        if int(update_json["versionCode"]) > int(item["versionCode"]):
                            self.upload_from_json(item, update_json)

                        if not c_file.exists():
                            self.upload_from_json(item, update_json)

                    else:
                        self.upload_from_json(item, update_json)

                elif item["update"].endswith("zip"):
                    if update_all:
                        self.upload_from_url(item)
            else:
                if item["update"].endswith("zip"):
                    u_file = self.local_folder.joinpath(item["update"])
                    if u_file.exists():
                        prop = get_props(u_file).dict
                        if "versionCode" in item:
                            c_file = self.cloud_file(item)
                            if int(prop["versionCode"]) > int(item["versionCode"]):
                                self.upload_from_local(item, u_file)

                            if not c_file.exists():
                                self.upload_from_local(item, u_file)

                        else:
                            self.upload_from_local(item, u_file)

            pro.progress_default()

    def update_json(self):
        self.json_dict["timestamp"] = str(datetime.now())
        self.json_dict["modules"] = self.json_list
        write_json(self.json_dict, self.json_file)

    def push(self):
        cwd_folder = self.modules_folder.parent

        msg = "timestamp: {0}".format(datetime.now())
        subprocess.run(['git', 'add', '.'], cwd=cwd_folder.as_posix())
        subprocess.run(['git', 'commit', '-m', msg], cwd=cwd_folder.as_posix())
        subprocess.run(['git', 'push', '-u', 'origin', REPO_BRANCH], cwd=cwd_folder.as_posix())


def main():
    root_folder = Path(__file__).resolve().parent
    sync = Sync(root_folder)
    sync.pull()
    sync.update_json()
    sync.push()


if __name__ == "__main__":
    main()
