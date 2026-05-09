import os
import shutil
import random
import sys
import json
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Randomise the assets of a Minecraft resource pack.')
parser.add_argument('-p', '--pack', default='pack', type=str, dest='pack', help='specifies a resource pack folder')
parser.add_argument('-s', '--seed', default=random.randrange(sys.maxsize), type=int, dest='seed', help='specifies a random seed')
#parser.add_argument('--noanimations', action='store_false', dest='animations', help='disables animations, fixes some missing textures')
parser.add_argument('--alttextures', action='store_true', dest='alttextures', help='alternative texture randomization, only swaps blocks with other blocks, items with items, etc. supports animated textures')
parser.add_argument('--notextures', action='store_false', dest='textures', help='disables randomised textures')
parser.add_argument('--noblockstates', action='store_false', dest='blockstates', help='disables randomised block states')
parser.add_argument('--nosounds', action='store_false', dest='sounds', help='disables randomised sounds')
parser.add_argument('--notexts', action='store_false', dest='texts', help='disables randomised text')
parser.add_argument('--nofonts', action='store_false', dest='fonts', help='disables randomised fonts')
parser.add_argument('--noshaders', action='store_false', dest='shaders', help='disables randomised shaders')
parser.add_argument('--install', action='store_true', dest='install', help='auto-install the shuffled pack to the Minecraft resourcepacks folder')
parser.add_argument('--nomodels', action='store_false', dest='models', help='EXPERIMENTAL: randomised block/item models')

args = parser.parse_args()

resourcepack = args.pack
randomseed = args.seed
randomisetextures = args.textures
randomisemodels = args.models
#randomiseanimations = args.animations
randomiseblockstates = args.blockstates
randomisesounds = args.sounds
randomisetext = args.texts
randomisefont = args.fonts
randomiseshaders = args.shaders
alttextures = args.alttextures
auto_install = args.install

random.seed(randomseed)

if resourcepack == "shuffle":
    print("The input resource pack may not be named 'shuffle'.")
    input('Press any key to exit.')
    sys.exit()
if os.path.exists(os.path.join('shuffle')):
    print("Please remove the 'shuffle' folder before running this program.")
    input('Press any key to exit.')
    sys.exit()

def makepath(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except:
            print('DEBUG: tried to create an existing folder')

if not (randomisetextures or randomisemodels or randomiseblockstates or randomisesounds or randomisetext or randomisefont or randomiseshaders):
    print('Successfully randomised nothing!')
    sys.exit()
if not os.path.exists(resourcepack):
    makepath(resourcepack)
    print('Unable to locate resource pack folder! Please make sure you have an extracted resource pack in the "'+resourcepack+'" folder.')
    input('Press any key to exit.')
    sys.exit()
if not os.path.exists(os.path.join(resourcepack, 'assets')):
    print('Unable to locate resource pack folder! Please ensure you have extracted one properly, you should have an "assets" folder in the "'+resourcepack+'" folder.')
    input('Press any key to exit.')
    sys.exit()

images = {}
randimages = {}
itemmodels = []
blockmodels = []
blockstates = []
sounds = []
randsounds = []
languages = []
specialtexts = []
shaders = {'vsh': [], 'fsh': [], 'json': []}
totaltextures = 0
longestbar = 0

def processimage(imagepath):
    #print(imagepath.replace('.png', '.mcmeta'))
    #if randomiseanimations or os.path.exists()
    if not alttextures:
        f = open(imagepath,mode='rb')
        header = f.read(26)
        f.close()
        width = int.from_bytes(header[16:20],'big',signed=False)
        height = int.from_bytes(header[20:24],'big',signed=False)
        dictkey = f"{width}x{height}"
        if dictkey not in images:
            images[dictkey] = []
        images[dictkey].append(imagepath)
    else:
        texturetype = imagepath.split(os.path.sep)[4]
        if texturetype not in images:
            images[texturetype] = []
        images[texturetype].append(imagepath)

#find the files to swap
for dirpath, dirs, files in os.walk(os.path.join(resourcepack,"assets")):
    for file in files:
        fullfilepath = os.path.join(dirpath,file)
        mcraft = os.path.join(resourcepack,'assets','minecraft')

        if file.endswith('.png') and (randomisefont or randomisetextures):
            if dirpath == os.path.join(mcraft,'textures','font') and randomisefont:
                processimage(fullfilepath)
                totaltextures += 1
            if dirpath != os.path.join(mcraft,'textures','font') and randomisetextures:
                processimage(fullfilepath)
                totaltextures += 1
        elif dirpath == os.path.join(mcraft,'models','item') and randomisemodels:
            itemmodels.append(fullfilepath)
        elif dirpath == os.path.join(mcraft,'models','block') and randomisemodels:
            blockmodels.append(fullfilepath)
        elif dirpath == os.path.join(mcraft,'blockstates') and randomiseblockstates:
            blockstates.append(fullfilepath)
        elif file.endswith('.ogg') and randomisesounds:
            sounds.append(fullfilepath)
        elif dirpath == os.path.join(mcraft,'lang') and randomisetext:
            languages.append(fullfilepath)
        elif dirpath == os.path.join(mcraft,'texts') and randomisetext:
            specialtexts.append(fullfilepath)
        elif dirpath == os.path.join(mcraft,'shaders','program') and randomiseshaders:
            shaders[file.split('.')[1]].append(fullfilepath)

print(f"Random Seed: {randomseed}")

tasks = []
randoimagery = randomisetextures or randomisefont
for resolution, imagefiles in images.items():
    if randoimagery and imagefiles:
        tasks.append((imagefiles, f"textures ({resolution})"))
if randomisemodels and itemmodels:
    tasks.append((itemmodels, "item models"))
if randomisemodels and blockmodels:
    tasks.append((blockmodels, "block models"))
if randomiseblockstates and blockstates:
    tasks.append((blockstates, "block states"))
if randomisesounds and sounds:
    tasks.append((sounds, "sounds"))
for key, value in shaders.items():
    if randomiseshaders and value:
        tasks.append((value, f"shaders ({key})"))

text_task = randomisetext and (languages or specialtexts)
total_steps = len(tasks) + (1 if text_task else 0)

with tqdm(total=total_steps, desc="Overall Progress") as overall_pbar:
    for toRando, inputType in tasks:
        with tqdm(total=len(toRando), desc=inputType) as pbar:
            shufflelist = list(toRando)
            random.shuffle(shufflelist)
            for i, orig_file in enumerate(toRando):
                filename = orig_file.split(os.path.sep)[-1]
                destfile = f'shuffled-{randomseed}'
                for newpath in orig_file.split(os.path.sep)[1:]:
                    destfile = os.path.join(destfile, newpath)

                makepath(destfile)
                shutil.copyfile(shufflelist[i], destfile)

                mcmeta = shufflelist[i] + '.mcmeta'
                mcdest = destfile + '.mcmeta'
                if os.path.exists(mcmeta):
                    shutil.copyfile(mcmeta, mcdest)

                pbar.set_postfix(file=filename)
                pbar.update(1)
        overall_pbar.update(1)

    if text_task:
        with tqdm(total=len(languages) + len(specialtexts), desc="Randomising text") as pbar:
            langvalues = []

            for lang in languages:
                with open(lang, encoding='utf-8') as f:
                    data = json.load(f)
                langvalues += list(data.values())

            for tfile in specialtexts:
                with open(tfile, encoding='utf-8') as f:
                    content = f.readlines()
                content = [x.strip() for x in content]
                langvalues += content

            for lang in languages:
                filename = lang.split(os.path.sep)[-1]
                with open(lang, encoding='utf-8') as f:
                    data = json.load(f)
                shufflelang = {}
                for key in list(data.keys()):
                    randindex = random.randint(0, len(langvalues)-1)
                    shufflelang[key] = langvalues[randindex]
                    del langvalues[randindex]
                destpath = f'shuffled-{randomseed}' + lang[4:]
                makepath(destpath)
                with open(destpath, 'w', encoding='utf-8') as output:
                    json.dump(shufflelang, output)
                pbar.set_postfix(file=filename)
                pbar.update(1)

            for tfile in specialtexts:
                filename = tfile.split(os.path.sep)[-1]
                with open(tfile, encoding='utf-8') as f:
                    content = f.readlines()
                linesadded = 0
                outputlines = []
                while linesadded < len(content):
                    randindex = random.randint(0, len(langvalues)-1)
                    outputlines.append(langvalues[randindex])
                    del langvalues[randindex]
                    linesadded += 1
                destpath = f'shuffled-{randomseed}' + tfile[4:]
                makepath(destpath)
                with open(destpath, 'w', encoding='utf-8') as output:
                    output.write('\n'.join(outputlines))
                pbar.set_postfix(file=filename)
                pbar.update(1)
        overall_pbar.update(1)

print("Creating meta files")
if "16x16" in images.keys():
    shutil.copyfile(random.choice(images["16x16"]), os.path.join(f'shuffled-{randomseed}', 'pack.png'))
elif os.path.exists(os.path.join(resourcepack,'pack.png')):
    shutil.copyfile(os.path.join(resourcepack,'pack.png'), os.path.join(f'shuffled-{randomseed}', 'pack.png'))

makepath(os.path.join(f'shuffled-{randomseed}', 'pack.mcmeta'))
with open(os.path.join(f'shuffled-{randomseed}', 'pack.mcmeta'), "w") as descfile:
    descfile.write('{"pack":{"pack_format":4,"description":"https://github.com/ElliNet13/minecraft-randomiser - MC Data Randomizer, Seed: '+str(randomseed)+'"}}')

if auto_install:
    print('Installing to resource pack folder')

    try:
        system = sys.platform.lower()
        if system.startswith('linux'):
            destfolder = os.path.expanduser(os.path.join('~', '.minecraft', 'resourcepacks', f'shuffle-{randomseed}'))
        elif system.startswith('darwin'):
            destfolder = os.path.expanduser(os.path.join('~', 'Library', 'Application Support', 'minecraft', 'resourcepacks', f'shuffle-{randomseed}'))
        elif system.startswith('win'):
            destfolder = os.path.expandvars(os.path.join('%APPDATA%', '.minecraft', 'resourcepacks', f'shuffle-{randomseed}'))
        else:
            destfolder = 'shuffle'
            print('Failed to identify operating system, placing file in current folder instead.')
        shutil.make_archive(destfolder, 'zip', f'shuffled-{randomseed}')
        print('Resource pack installed!')
        shutil.rmtree('shuffled')
    except:
        print('Compression failed! Please manually move the "shuffled" folder to your resource pack folder.')
else:
    print('Creating shuffled pack archive')
    try:
        shutil.make_archive('shuffle', 'zip', f'shuffled-{randomseed}')
        print(f'Shuffled pack created as shuffle-{randomseed}.zip')
        shutil.rmtree('shuffled')
    except:
        print('Compression failed! The "shuffled" folder contains the randomized pack.')
