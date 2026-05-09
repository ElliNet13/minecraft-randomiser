import requests
import zipfile
import argparse
import shutil
import os
from tqdm import tqdm

def grab_minecraft_manifest():
    manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
    response = requests.get(manifest_url)
    response.raise_for_status()
    return response.json()

def grab_jar_url(version_info):
    version_url = version_info['url']
    response = requests.get(version_url)
    response.raise_for_status()
    version_data = response.json()
    return version_data['downloads']['client']['url']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download a Minecraft resource and data pack.')
    parser.add_argument('version', type=str, help='The version of Minecraft to download the resource pack for.')
    args = parser.parse_args()

    print('Downloading Minecraft manifest...')
    manifest = grab_minecraft_manifest()
    for version_info in manifest['versions']:
        if version_info['id'] == args.version:
            jar_url = grab_jar_url(version_info)
            print(f'Downloading Minecraft {args.version} from {jar_url}')
            response = requests.get(jar_url)
            response.raise_for_status()
            with open('minecraft.jar', 'wb') as f:
                f.write(response.content)
            print('Download complete!')
            break
    else:
        print(f'Version {args.version} not found in manifest.')
    
    shutil.rmtree('pack', ignore_errors=True)
    shutil.rmtree('data', ignore_errors=True)

    with zipfile.ZipFile('minecraft.jar', 'r') as jar:
        for member in tqdm(jar.namelist(), desc='Extracting files'):
            if member.startswith('assets/'):
                jar.extract(member, 'pack')
            elif member.startswith('data/'):
                jar.extract(member, 'data')

    os.remove('minecraft.jar')

    print('Download complete!')