# Minecraft Randomiser

This is a set of programs to randomise data about Minecraft.

Requires Python 3.6+ to run.

## `pack_downloader.py`

This downloads the Minecraft resource and data packs from Minecraft servers. Run before other scripts.

### Usage

Run `pack_downloader.py -h` to get the program's help and list of options.

`python3 pack_downloader.py 1.16` - Download the resource pack and data pack for Minecraft 1.16.

## `resource_randomiser.py`

This randomises every single image, sound, shader, and language file of a resource pack and automatically installs it into your resource pack folder.

### Usage

To use, simply run `resource_randomiser.py` in python3, or double click the executable file. Options can be viewed from the command line using `resource_randomiser.py -h`

#### Examples

`python3 resource_randomiser.py -h` - Get the program's help and list of options.

`python3 resource_randomiser.py` - Randomises the resource pack from the "pack" folder with all default randomisation settings.

`python3 resource_randomiser.py --pack faithful` - Randomises the resource pack from the "faithful" folder.

`python3 resource_randomiser.py --notextures --nosounds --pack faithful` - Randomise everything except the textures and sounds from the resource pack in the "faithful" folder.

## `data_randomiser.py`

This randomises the Minecraft data pack, which includes files such as loot tables for random block drops, recipes, advancements, and experimentally structures (disabled by default, some configurations crash).

### Usage

`python3 data_randomiser.py -h` - Get the program's help and list of options.

`python3 data_randomiser.py` - Randomises loot tables, recipes, and advancements.

`python3 data_randomiser.py --norecipes --structures` - Enables structure randomisation and disables recipes.

`python3 data_randomiser.py --randomlootamount 64` - Items can drop up to 64 times (not amount of items but rather amount of loot)

`python3 data_randomiser.py --norecipes --noloottables --notags --noadvancements --randomlootamount 256` - Literally just Minecraft but loots are randomly generated up to 4 stacks

## Bugs

Please report bugs in the [issue](https://github.com/ElliNet13/minecraft-randomiser/issues) tab.