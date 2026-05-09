import requests
import zipfile
import argparse
import shutil
import os
import signal
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

ASSETS_BASE = "https://resources.download.minecraft.net/"
STOP_EVENT = threading.Event()


def handle_sigint(signum, frame):
    if not STOP_EVENT.is_set():
        print("\nInterrupted by user. Stopping...")
        STOP_EVENT.set()


signal.signal(signal.SIGINT, handle_sigint)

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

def download_single_asset(args):
    key, value, output_dir = args

    hash = value["hash"]
    subdir = hash[:2]
    url = f"{ASSETS_BASE}{subdir}/{hash}"

    dest = os.path.join(output_dir, "assets", key.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if STOP_EVENT.is_set():
        return False

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        with open(dest, "wb") as f:
            f.write(r.content)

        return True

    except Exception as e:
        if STOP_EVENT.is_set():
            return False
        print(f"Failed: {key} -> {e}")
        return False


def download_assets(asset_index, output_dir="pack", workers=12):
    objects = asset_index["objects"]

    print(f"Downloading {len(objects)} assets with {workers} threads...")

    tasks = [(k, v, output_dir) for k, v in objects.items()]
    total = len(tasks)

    done = 0
    success = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(download_single_asset, t) for t in tasks]

        try:
            for f in tqdm(as_completed(futures), total=total, desc="Assets"):
                result = f.result()
                done += 1
                if result:
                    success += 1
        except KeyboardInterrupt:
            STOP_EVENT.set()
            print("\nInterrupted during asset download. Waiting for workers to stop...")
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:
                executor.shutdown(wait=False)

    print(f"Assets done: {success}/{total}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Minecraft assets + packs.")
    parser.add_argument("version", type=str)
    parser.add_argument("-w", "--workers", type=int, default=30, help="Number of threads to use for downloading assets.")
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
    download_assets(asset_index, "pack", workers=args.workers)

    print("Done.")