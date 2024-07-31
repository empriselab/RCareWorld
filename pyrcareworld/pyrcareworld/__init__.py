# Version of the library that will be used to upload to pypi
__version__ = "1.5.0"

import os.path
import json
import threading
from pyrcareworld.utils.locker import Locker
from pyrcareworld.utils.version import Version

try:
    import requests
except:
    pass

def check_for_updates():
    try:
        # todo: change the package name
        response = requests.get(f'https://pypi.org/pypi/pyrcareworld/json')
        response.raise_for_status()
        data = response.json()
        current_version = Version(__version__)

        versions = Version.sorted([Version(i) for i in data['releases']], reverse=True)
        for i in versions:
            if i[0] == current_version[0] and i[1] == current_version[1] and i[2] == current_version[2]:
                if i[3] > current_version[3]:
                    print(f'\033[33mThere is a new patch version available: {i}, please consider upgrading!\033[0m')
                    break
    except Exception as e:
        print(e)


def read_config():
    if not os.path.exists(config_path):
        new_config = {"assets_path": "", "executable_file": ""}
        save_config(new_config)
    with Locker("config"):
        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)


def save_config(config: dict):
    assert "assets_path" in config and "executable_file" in config
    with Locker("config"):
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=True)


user_path = os.path.expanduser("~/.rcareworld")
os.makedirs(user_path, exist_ok=True)
config_path = os.path.join(user_path, "config.json")
config = read_config()
assets_path = config["assets_path"]
executable_file = config["executable_file"]

try:
    update_thread = threading.Thread(target=check_for_updates)
    update_thread.daemon = True
    update_thread.start()
except:
    pass
