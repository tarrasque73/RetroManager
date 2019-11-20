# RetroManager

## Simple utility to manage RetroArch overlay images and related config files


###Installation

Download the zip file and uncompress wherever you want.

The program is written in Python3 so you'll need the Python language 3.* installed on your system. The program is then OS independent and should work fine on Linux, Mac or Windows.

###Configuration

Rename the default configuration file to "config.ini". The file contains the basic paths for the utility to work.

The "realoverlaybasedir" key MUST point to the path where RetroArch will look for overlay files. This is most important because it's the path that will be written into the configuration files. If it's incorrect RetroArch will not be able to locate and show the overlays. If you see the game running in a small box in RetroArch surrounded by black you probably put an incorrect path in this variable.

All "output" directories will be created automatically if non existant. PLEASE NOTE THAT ALL FILES EVENTUALLY EXISTING WILL BE DELETED.

Every basic command that needs input files has it's own "input" keys in its related section. Currently the "overlay_*" and "config_*" commands need to scan the directory containing the original overlays. More on this later. Nothing in this folder will be menipulated or deleted (unless it's an output folder for some other command).

The "templates" directory contains the base templates udes to generate the configuration files. 

TODO

Write help on how to edit and customized the default templates.

###Usage

Basic syntax: "python retromanager.py <command> <additional parameters>"

Launch "python retromanager.py -h" for full help.

Where:

Current supported parameters are: overlay_resize, config_generate, shader_generate, generate_all
 
####overlay_resize

Resizes an overlay from the input folder to the output folder and generates the corresponding .cfg file according to the template. for our purposes, "overlay" is any PNG image that contains a sqar(ish) transparent or mostly transparent area in the middle, which we refer to as "viewport". All resize operations keep the aspect ratio of the original image.

Basic syntax: "python retromanager.py overlay_resize <core> <gamename> <additional parameters>" 

The command looks for input file <gamename>.png in the input directory, detects the size of the viewport and scales it depending on the additional parameters if needed, before saving it in the output folder.

Parameters:

- -tx and -ty set the targes size of the resized overlay. If not provided they default to the original dimensions.

- -tm sets the "mode" of the resize operation, and can be either of "outer" or "inner". Outer means that the dimensions of the original overay taken into account for resizing are the dimensions of the full image. Inner means that the dimensions of the viewport are taken into account instead. This is usefulwhen you want to maximise the play area of the game on your screen. In this case some part of the overlay will be cropped. the default is "outer"

- -mx and -my set the margins of the resize operation. Are mostly used combined with "-rm inner" in ordae to leave some of the overlay visible around the resized viewport. They don't have much use with "-rm outer" unless you want to let some of the background visible. Defaults are zero.

- -bc sets the background color for the resized overlay before the resized image is pasted on it. It's expressed in hexadecimal values. Default value is "000000" (black).

NOTE: when -tx, -ty and -rm are all missing or set to default the original overlay is just copied to the destination and it's not subject to any resize operation.

Examples: 

python retromanager.py "MAME 2016" pacman

Simple copy of overlay into output folder and configuration file generation

python retromanager.py "MAME 2016" pacman -rm inner

Resize overlay maximising the viewport area in an overlay with the same size of the original, all excess parts cropped.

python retromanager.py "MAME 2016" pacman -rm inner -mx 100 - my 100

Resize overlay in an overlay with the same size of the original, leaving 100 pixels of margin around the viewport.

python retromanager.py "MAME 2016" pacman -rm inner -mx 100 - my 100 - tx 1920 - ty 1080 -bc FFFFFF

As above, but resized overlay will be 1920x1080 pixels. If the aspect ratio of the original overlay and the resized overlay differ, any excess area will be white.

####config_generate

Generates the configuration files for RetroArch. These are game dependant and must be copied in the folder where RetroArch expects to find them, which includes the core name in the path

The most important feature of this function is setting the parameters that RetroArch uses to resize the actual game screen size by detecting the viewport area of the overlay file of the same name found in the input folder.

This means that you can easily set games in RetroArch so that the game screen size matches the viewport of your overlays!

NOTE: an effective way to use this command is setting the output folder of "overlay_resize" as the input folder of "config_generate". You can then run the 2 commands in sequence. It's even easier to run "generate_all" (discussed later).

TODO

Continue documentation

####shader_generate

Generates RetroArch shader preset files.

TODO

Continue documentation

####generate_all

Runs "overlay_resize", "gonfig_generate" and "shader_generate" in sequence.

TODO

Continue documentation



