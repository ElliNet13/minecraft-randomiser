import requests
import zipfile
import argparse
import shutil
import os
from tqdm import tqdm
import json

ASSETS_BASE = "https://resources.download.minecraft.net/"

def grab_minecraft_manifest():
    url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def grab_version_json(version_info):
    r = requests.get(version_info["url"])
    r.raise_for_status()
    return r.json()

def download_file(url, path):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def download_assets(asset_index, output_dir="pack"):
    objects = asset_index["objects"]

    print(f"Downloading {len(objects)} assets...")

    for key, value in tqdm(objects.items(), desc="Assets"):
        hash = value["hash"]
        subdir = hash[:2]
        url = f"{ASSETS_BASE}{subdir}/{hash}"

        dest = os.path.join(output_dir, "assets", key.replace("/", os.sep))
        download_file(url, dest)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Minecraft assets + packs.")
    parser.add_argument("version", type=str)
    args = parser.parse_args()

    print("Downloading manifest...")
    manifest = grab_minecraft_manifest()

    version_info = next((v for v in manifest["versions"] if v["id"] == args.version), None)

    if not version_info:
        print(f"Version {args.version} not found.")
        exit(1)

    print("Downloading version metadata...")
    version_json = grab_version_json(version_info)

    # ---- ASSET INDEX ----
    asset_index_url = version_json["assetIndex"]["url"]
    print("Downloading asset index...")

    r = requests.get(asset_index_url)
    r.raise_for_status()
    asset_index = r.json()

    shutil.rmtree("pack", ignore_errors=True)
    shutil.rmtree("data", ignore_errors=True)

    # ---- DOWNLOAD JAR ----
    jar_url = version_json["downloads"]["client"]["url"]
    print(f"Downloading JAR: {jar_url}")

    r = requests.get(jar_url)
    r.raise_for_status()

    with open("minecraft.jar", "wb") as f:
        f.write(r.content)

    # ---- EXTRACT DATA + ORIGINAL ASSETS FOLDER ----
    with zipfile.ZipFile("minecraft.jar", "r") as jar:
        for member in tqdm(jar.namelist(), desc="Extracting JAR"):
            if member.startswith("data/"):
                jar.extract(member, "data")
            elif member.startswith("assets/"):
                jar.extract(member, "pack")

    os.remove("minecraft.jar")

    # ---- DOWNLOAD ASSET OBJECTS ----
    download_assets(asset_index, "pack")

    print("Done.")