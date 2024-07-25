import os
import sys
import tempfile
import zipfile
from sys import platform
import argparse
import requests
import pyrcareworld
from pyrcareworld.utils.version import Version


def pyrcareworld_entry_points():
    print("pyrcareworld entry points")
    parser = argparse.ArgumentParser(description='rcareworld entry points')
    subparsers = parser.add_subparsers(dest='command', help='download/etc')
    parser_download = subparsers.add_parser('download', help='Download rcareworld release')
    parser_download.add_argument('-s', '--savepath', type=str, help='rcareworld release save path')
    parser_download.add_argument('-v', '--version', type=str, help='rcareworld release Version')
    args = parser.parse_args()
    if args.command == 'download':
        download(args)


def download(args):
    if args.savepath is None:
        save_path = os.path.expanduser(r"~/rcareworld")
    else:
        save_path = args.savepath

    releases_url = f"https://api.github.com/repos/empriselab/RCareWorld/releases"
    response = requests.get(releases_url)
    releases = response.json()
    last_version = None

    if args.version is None:
        current_version = Version(pyrcareworld.__version__)
        for i in releases:
            if "v" not in i["tag_name"] and "." not in i["tag_name"]:
                continue
            version = Version(i["tag_name"].replace("v", ""))
            if version[0] == current_version[0] and version[1] == current_version[1] and version[2] == current_version[2]:
                if last_version is None:
                    last_version = version
                elif version[3] > current_version[3]:
                    last_version = version
    else:
        current_version = Version(args.version)
        for i in releases:
            if "v" not in i["tag_name"] and "." not in i["tag_name"]:
                continue
            version = Version(i["tag_name"].replace("v", ""))
            if version == current_version:
                last_version = version

    if last_version is None:
        print("No available version found")
        return

    if platform == "win32":
        platform_string = "Windows"
        suffix = ".exe"
    elif platform == "linux":
        platform_string = "Linux"
        suffix = ".x86_64"
    else:
        raise EnvironmentError(f"Unsupported systems: {platform}")

    download_url = None
    for i in releases:
        if i["tag_name"] == f"v{last_version}":
            for asset in i["assets"]:
                if platform_string in asset["name"]:
                    download_url = asset["browser_download_url"]
                    download_size = asset["size"]
                    break
            break

    if download_url is None:
        print("No available version found")
        return

    temp_path = os.path.join(tempfile.gettempdir(), "temp_rfu_release.zip")
    with requests.get(download_url, stream=True) as response:
        print(f"Downloading: {download_url}")
        print(f"---")
        length = 0
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024000):
                length = length + 1024000
                f.write(chunk)
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                print(f"{length}/{download_size}---{int(length * 100 / download_size)}%")

    os.makedirs(save_path, exist_ok=True)
    with zipfile.ZipFile(temp_path, 'r') as zipObject:
        zipObject.extractall(save_path)
    folder_name = os.path.splitext(os.path.basename(download_url))[0]
    folder_path = os.path.join(save_path, folder_name)
    print(fr"Unzip Done: {folder_path}")
    executable_file = os.path.abspath(os.path.join(folder_path, f"RCareWorld{suffix}"))
    pyrcareworld.config["executable_file"] = executable_file
    pyrcareworld.save_config(pyrcareworld.config)
    if platform == "linux":
        os.system(f"chmod +x {executable_file}")
    print(fr"Write config executable_file: {executable_file}")
