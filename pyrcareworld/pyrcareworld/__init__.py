# Version of the library that will be used to upload to pypi
__version__ = "1.1.0"

import os.path
import json


def read_config():
    if not os.path.exists(config_path):
        config = {}
        config["assets_path"] = ""
        config["executable_file"] = ""
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=True)
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


user_path = os.path.expanduser("~/.rfuniverse")
if not os.path.exists(user_path):
    os.makedirs(user_path)
config_path = os.path.join(user_path, "config.json")
config = read_config()
assets_path = config["assets_path"]
executable_file = config["executable_file"]
