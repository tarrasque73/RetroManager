# RetroManager

## Simple utility to manage RetroArch overlay images and related config files


### Installation

Download the zip file and uncompress wherever you want.

The program is written in Python3 so you'll need the Python language 3.* installed on your system. The program is then OS independent and should work fine on Linux, Mac or Windows.

### Configuration

Rename the default configuration file to "config.ini". The file contains the basic paths for the utility to work.

The "realoverlaybasedir" key MUST point to the path where RetroArch will look for overlay files. This is most important because it's the path that will be written into the configuration files. If it's incorrect RetroArch will not be able to locate and show the overlays. If you see the game running in a small box in RetroArch surrounded by black you probably put an incorrect path in this variable.

All "output" directories will be created automatically if non existant. PLEASE NOTE THAT ALL FILES EVENTUALLY EXISTING WILL BE DELETED.

Every basic command that needs input files has it's own "input" keys in its related section. Currently the "overlay_*" and "config_*" commands need to scan the directory containing the original overlays. More on this later. Nothing in this folder will be menipulated or deleted (unless it's an output folder for some other command).

The "templates" directory contains the base templates udes to generate the configuration files. When generating files, the commands look for a template file named like the game (f.i. pacman.lay or pacman.cfg) in the appropriate template directory. If they can’t find it then they’ll look for a default template named “_default.lay” or whatever. This way you can have specific templates for games whose configurations are non standard.

*TODO*

Expand help on how to edit and customized the default templates.

### Usage

	Basic syntax: `python retromanager.py <command> <additional parameters>`

Launch `python retromanager.py -h` for full help.

Current supported commands are: bezel_resize, layout_generate, config_generate, shader_generate, generate_all
 
#### bezel_resize

Resizes a bezel from the input folder to the output folder. For our purposes, "bezel" is any PNG image that contains a rectangular transparent or mostly transparent area in the middle, which we refer to as "viewport". All resize operations keep the aspect ratio of the original image.

	Basic syntax: `python retromanager.py overlay_resize <core> <gamename> <additional parameters>` 

The command looks for input file <gamename>.png in the input directory, detects the size of the viewport and scales it depending on the additional parameters if needed, before saving it in the output folder.

Parameters:

- `-tx` and `-ty` set the target size of the resized bezel. If not provided they default to the original dimensions.

- `-tm` sets the "mode" of the resize operation, and can be "outer", "inner" or "custom". Default is "outer"

	- `outer` mode resizes the bezel based on the dimensions of the original image. Useful when you already have your bezels in the correct dimensions and you're only interested in viewport detection for config files generation.

	- `inner` mode resizes the bezel based on the dimensions of the viewport. Useful when you want to maximise the play area of the game on your monitor. In this case some part of the bezel will be cropped.

	- `custom` mode is similar to inner mode but lets you specify the size of the resized viewport explicitly with parameters `-cx` and `-cy` instead of fitting it in the target size, with optional margins. It's particularly useful when you want all the resized viewport to have the same size, whether they are horizontal or vertical (see examples, below).

- `-cx` and `-cy` set the intended size of the resized viewport for mode `outer`. They are ignored for other resize modes. If not provided they default to the original dimensions.

- `-mx` and `-my` set the margins of the resize operation. they are usually used combined with `-rm inner` in order to leave some of the bezel visible around the resized viewport. They don't have much use with `-rm outer` unless you want to let some of the background visible. They are ignored with `-rm custom`. Defaults are 0.

- `-bc` sets the background color for the resized bezel before the resized image is pasted on it. It's expressed in hexadecimal values. Default value is "000000" (black).

- `-tt` sets the pixel padding to leave around the detected viewport. It might be necessary to fine tune the value to avoid overlapping with some bezels, expecially if strongly curved. Default value is 3 pixels.

- `-pd` sets the transparency threshold for the viewport detection mechanism. It's expressed in a value ranging from 0 (fully opaque) to 255 (fully transparent). Default value is 200.

NOTE: when `-tx`, `-ty` and `-rm` are all missing or set to default the original bezel is just copied to the destination and it's not subject to any resize operation, so the process is faster.

Examples: 

`python retromanager.py "MAME 2016" pacman`

Simple copy of bezel into output folder and configuration file generation

`python retromanager.py "MAME 2016" pacman -rm inner`

Resize bezel maximising the viewport area in an bezel with the same size of the original, all excess parts cropped.

`python retromanager.py "MAME 2016" pacman -rm inner -mx 100 - my 100`

Resize bezel to a bezel with the same size of the original, leaving 100 pixels of margin around the viewport.

`python retromanager.py "MAME 2016" pacman -rm inner -mx 100 - my 100 - tx 1920 - ty 1080 -bc FFFFFF`

As above, but resized bezel will be 1920x1080 pixels. If the aspect ratio of the original bezel and the resized bezel differ, any excess area will be white.

`python retromanager.py "MAME 2016" blktiger -rm custom -cx 1000 -cy 1000 -tx 1920 -ty 1080`

`python retromanager.py "MAME 2016" gyruss -rm custom -cx 1000 -cy 1000 -tx 1920 -ty 1080`

In this examples, the two bezels have different orientations because the first game has an horizontal screen and the second vertical. The commands produce new bezels where the viewports have the same maximum dimension. 

#### config_generate

Generates the configuration files for RetroArch. These are game dependant and must be copied in the folder where RetroArch expects to find them, which includes the core name in the path

The most important feature of this function is setting the parameters that RetroArch uses to resize the actual game screen size by detecting the viewport area of the overlay file of the same name found in the input folder. This means that you can easily set games in RetroArch so that the game screen size matches the viewport of your overlays!

NOTE: an effective way to use this command is setting the output folder of `overlay_resize` as the input folder of `config_generate`. You can then run the 2 commands in sequence. It's even easier to run `generate_all` (discussed later).

*TODO*

Continue documentation

#### layout_generate

Similar to `config_generate` but in respect to MAME style layout files.

*TODO*

Continue documentation

#### shader_generate

Generates RetroArch shader preset files.

*TODO*

Continue documentation

#### generate_all

Runs `overlay_resize`, `config_generate`, `layout_generate` and `shader_generate` in sequence.

*TODO*

Continue documentation



