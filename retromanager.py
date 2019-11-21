import os
import getopt
import sys
import configparser
import overlaymanager

config = []

def readConfig(file):
	if (not os.path.exists(file)):
		print('ERROR: Missing configuration file: %s' % file)
		exit(-1)

	global config
	config = configparser.ConfigParser()
	config.read(file)

	if ('general' not in config):
		print('ERROR: Missing configuration section: [general]')
		exit(-1)
	if ('realoverlaybasedir' not in config['general']):
		print('ERROR: Missing configuration key: [general] realoverlaybasedir')
		exit(-1)
	
def setupUsage():
	import argparse
	parser = argparse.ArgumentParser(description="Library to generate and manipulate overlay image files and other configuration files for the RetroArch emulator frontend.")
	parser.add_argument("-c", "--config", help="Configuration file (default: config.ini)", default="config.ini")

	parent_parser = argparse.ArgumentParser(add_help=False)
	parent_parser.add_argument("core", help="The RetroArch core")
	parent_parser.add_argument("gamename", help="The MAME game name")
	
	subparsers = parser.add_subparsers(dest='command', title='commands', description='valid commands', help='add -h after the command name to display help about the command')
	
	parser_overlay_resize = subparsers.add_parser('overlay_resize', description="Resize overlay images and generate related configuration files", help="Resize overlay files", parents=[parent_parser])
	parser_overlay_resize.add_argument("-tx", "--targetsizex", type=int, default=0, help="target X size of the generated overlay")
	parser_overlay_resize.add_argument("-ty", "--targetsizey", type=int, default=0, help="target Y size of the generated overlay")
	parser_overlay_resize.add_argument("-mx", "--marginx", type=int, default=0, help="left and right margins of the generated overlay")
	parser_overlay_resize.add_argument("-my", "--marginy", type=int, default=0, help="top and bottom margins of the generated overlay")
	parser_overlay_resize.add_argument("-rm", "--resizemode", type=str, default='outer', choices=['inner', 'outer'], help="mode of the resizing of the overlay")
	parser_overlay_resize.add_argument("-bc", "--backgroundcolor", type=str, default='000000', help="background color")
	
	parser_config_generate = subparsers.add_parser('config_generate', description="Generate RetroArch configuration files", help="Generate configuration files", parents=[parent_parser])
	
	parser_shader_generate = subparsers.add_parser('shader_generate', description="Generate shader configuration files", help="Generate shader files", parents=[parent_parser])

	parser_generate_all = subparsers.add_parser('generate_all', description="Performs config_generate, overlay_generate, shader_generate", help="Generate all files", parents=[parent_parser])
	parser_generate_all.add_argument("-tx", "--targetsizex", type=int, default=0, help="target X size of the generated overlay")
	parser_generate_all.add_argument("-ty", "--targetsizey", type=int, default=0, help="target Y size of the generated overlay")
	parser_generate_all.add_argument("-mx", "--marginx", type=int, default=0, help="left and right margins of the generated overlay")
	parser_generate_all.add_argument("-my", "--marginy", type=int, default=0, help="top and bottom margins of the generated overlay")
	parser_generate_all.add_argument("-rm", "--resizemode", type=str, default='outer', choices=['inner', 'outer'], help="mode of the resizing of the overlay")
	parser_generate_all.add_argument("-bc", "--backgroundcolor", type=str, default='000000', help="background color")

	args = parser.parse_args()
	
	if not vars(args):
		parser.print_help()
		parser.exit(1)	
		
	return args

def main():
	args = setupUsage()
	print(args)
	readConfig(args.config)

	if 'config_generate' == args.command:
		overlaymanager.genCfg(args.core, args.gamename, config)
	elif 'shader_generate' == args.command:
		overlaymanager.genShader(args.core, args.gamename, config)
	elif 'generate_all' == args.command:
		overlaymanager.resize(args.core, args.gamename, args.targetsizex, args.targetsizey, args.marginx, args.marginy, args.resizemode, args.backgroundcolor, config)
		overlaymanager.genCfg(args.core, args.gamename, config)
		overlaymanager.genShader(args.core, args.gamename, config)
	elif 'overlay_resize' == args.command:
		overlaymanager.resize(args.core, args.gamename, args.targetsizex, args.targetsizey, args.marginx, args.marginy, args.resizemode, args.backgroundcolor, config)
	else:
		print('Command not supported')
		return -1
		
if __name__ == '__main__':
	#print("Start program\n")
	main()
	#print("\nEnd program")