import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime

from object import dict_, list_
from file import load_json, load_json_url, write_json, get_props, download_by_requests
from progress import Progress

GITHUB_RAW_URL = "https://raw.githubusercontent.com"
MODULE_REPO = "ya0211/magisk-modules-repo"
REPO_BRANCH = "main"
REPO_URL = "{0}/{1}/{2}".format(GITHUB_RAW_URL, MODULE_REPO, REPO_BRANCH)


def have_update_json(item, file):
    update_json = load_json_url(item.updateJson).dict_

    if "versionCode" in item:
        if int(update_json.versionCode) > int(item.versionCode):
            download_by_requests(update_json.zipUrl, file)
            update_info(item, file)
            shutil.move(file, file.parent.joinpath("{0}.zip".format(item.version.replace(" ", "_"))))

            item.status = {
                "zipUrl": "{0}/{1}/{2}.zip".format(REPO_URL, item.id, item.version.replace(" ", "_")),
                "changelog": update_json.changelog
            }

    elif not file.exists():
        download_by_requests(update_json.zipUrl, file)
        update_info(item, file)
        shutil.move(file, file.parent.joinpath("{0}.zip".format(item.version.replace(" ", "_"))))

        item["status"] = {
            "zipUrl": "{0}/{1}/{2}.zip".format(REPO_URL, item.id, item.version.replace(" ", "_")),
            "changelog": update_json.changelog
        }


def update_info(item: dict_, file: Path):
    prop = get_props(file).dict_
    item.name = prop.name
    item.version = prop.version
    item.versionCode = prop.versionCode
    item.author = prop.author
    item.description = prop.description


def pull(json_dict: dict_, modules_folder: Path, json_file: Path, update_all=True):
    json_list = list_(json_dict.modules).dict2dict_

    pro = Progress(json_list.size, bar_length=60)
    for item in json_list:

        item_dir = modules_folder.joinpath(item.id)
        if not item_dir.exists():
            os.makedirs(item_dir)
        else:
            for file in sorted(glob("{0}/*".format(item_dir))):
                os.remove(file)

        file = item_dir.joinpath("{0}.zip".format(item.id))

        if item.updateJson != "":
            have_update_json(item, file)

        else:
            if update_all:
                download_by_requests(item.status.get("zipUrl"), file)
                update_info(item, file)
                os.remove(file)

        pro.progress_default()

    json_dict.timestamp = str(datetime.now())
    json_dict.modules = json_list.dict_2dict
    write_json(json_dict.dict, json_file)


def push(cwd_folder: Path):
    msg = "timestamp: {0}".format(datetime.now())
    subprocess.run(['git', 'add', '.'], cwd=cwd_folder.as_posix())
    subprocess.run(['git', 'commit', '-m', msg], cwd=cwd_folder.as_posix())
    subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=cwd_folder.as_posix())


def main():
    root_folder = Path(__file__).resolve().parent
    modules_folder = root_folder.parent.joinpath("modules")
    json_folder = root_folder.parent.joinpath("json")
    file = json_folder.joinpath("modules.json")

    json_dict = load_json(file).dict_

    pull(json_dict, modules_folder, file)
    push(root_folder.parent)


if __name__ == "__main__":
    main()
