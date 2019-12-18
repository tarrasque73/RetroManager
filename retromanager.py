import os
import getopt
import sys
import configparser
import logging
import overlaymanager

config = []
logger = logging.getLogger(__name__)

def readConfig(file,logger):
	if (not os.path.exists(file)):
		logger.error('Missing configuration file: %s' % file)
		exit(-1)

	global config
	config = configparser.ConfigParser()
	config.read(file)

	if ('general' not in config):
		logger.error('Missing configuration section: [general]')
		exit(-1)
	if ('realoverlaybasedir' not in config['general']):
		logger.error('Missing configuration key: [general] realoverlaybasedir')
		exit(-1)

def setupLogging(logger):
	#logging.basicConfig(level=logging.INFO)
	logging.getLogger().setLevel(logging.DEBUG)
	
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_format = logging.Formatter('%(levelname)s - %(message)s')
	console_handler.setFormatter(console_format)
	
	logger.addHandler(console_handler)

def setupUsage(logger):
	import argparse
	parser = argparse.ArgumentParser(description="Library to generate and manipulate overlay image files and other configuration files for the RetroArch emulator frontend.")
	parser.add_argument("-c", "--config", help="Configuration file (default: config.ini)", default="config.ini")

	parent_parser = argparse.ArgumentParser(add_help=False)
	parent_parser.add_argument("core", help="The RetroArch core")
	parent_parser.add_argument("gamename", help="The MAME game name")
	
	subparsers = parser.add_subparsers(dest='command', title='commands', description='valid commands', help='add -h after the command name to display help about the command')
	
	parser_bezel_resize = subparsers.add_parser('bezel_resize', description="Resize bezel images", help="Resize bezel images", parents=[parent_parser])
	parser_bezel_resize.add_argument("-tx", "--targetsizex", type=int, default=0, help="target X size of the generated bezel")
	parser_bezel_resize.add_argument("-ty", "--targetsizey", type=int, default=0, help="target Y size of the generated bezel")
	parser_bezel_resize.add_argument("-mx", "--marginx", type=int, default=0, help="left and right margins of the generated bezel")
	parser_bezel_resize.add_argument("-my", "--marginy", type=int, default=0, help="top and bottom margins of the generated bezel")
	parser_bezel_resize.add_argument("-rm", "--resizemode", type=str, default='outer', choices=['inner', 'outer'], help="mode of the resizing of the bezel")
	parser_bezel_resize.add_argument("-bc", "--backgroundcolor", type=str, default='000000', help="background color")
	parser_bezel_resize.add_argument("-tt", "--transparency", type=int, default=200, help="transparency threshold for bezel detection")
	parser_bezel_resize.add_argument("-pd", "--padding", type=int, default=3, help="padding between viewport and bezel")
	
	parser_overlay_generate = subparsers.add_parser('overlay_generate', description="Generate RetroArch overlay configuration files", help="Generate RetroArch overlay configuration files", parents=[parent_parser])

	parser_layout_generate = subparsers.add_parser('layout_generate', description="Generate MAME layout configuration files", help="Generate MAME layout configuration files", parents=[parent_parser])
	parser_layout_generate.add_argument("-tt", "--transparency", type=int, default=200, help="transparency threshold for bezel detection")
	parser_layout_generate.add_argument("-pd", "--padding", type=int, default=3, help="padding between viewport and bezel")

	parser_config_generate = subparsers.add_parser('config_generate', description="Generate RetroArch core configuration files", help="Generate RetroArch core configuration files", parents=[parent_parser])
	parser_config_generate.add_argument("-tt", "--transparency", type=int, default=200, help="transparency threshold for bezel detection")
	parser_config_generate.add_argument("-pd", "--padding", type=int, default=3, help="padding between viewport and bezel")

	parser_shader_generate = subparsers.add_parser('shader_generate', description="Generate shader configuration files", help="Generate shader files", parents=[parent_parser])

	parser_generate_all = subparsers.add_parser('generate_all', description="Performs resize, config_generate, shader_generate, overlay_generate, layout_generate", help="Generate all configuration files and images", parents=[parent_parser])
	parser_generate_all.add_argument("-tx", "--targetsizex", type=int, default=0, help="target X size of the generated bezel")
	parser_generate_all.add_argument("-ty", "--targetsizey", type=int, default=0, help="target Y size of the generated bezel")
	parser_generate_all.add_argument("-mx", "--marginx", type=int, default=0, help="left and right margins of the generated bezel")
	parser_generate_all.add_argument("-my", "--marginy", type=int, default=0, help="top and bottom margins of the generated bezel")
	parser_generate_all.add_argument("-rm", "--resizemode", type=str, default='outer', choices=['inner', 'outer'], help="mode of the resizing of the bezel")
	parser_generate_all.add_argument("-bc", "--backgroundcolor", type=str, default='000000', help="background color")
	parser_generate_all.add_argument("-tt", "--transparency", type=int, default=200, help="transparency threshold for viewport detection")
	parser_generate_all.add_argument("-pd", "--padding", type=int, default=3, help="padding between viewport and bezel")

	args = parser.parse_args()
	
	if not vars(args):
		parser.print_help()
		parser.exit(1)	
		
	return args

def main():
	global logger

	args = setupUsage(logger)
	logger.debug(args)
	readConfig(args.config, logger)

	if 'config_generate' == args.command:
		overlaymanager.generateCfg(args.core, args.gamename, args.transparency, args.padding, config, logger)
	elif 'shader_generate' == args.command:
		overlaymanager.generateShader(args.core, args.gamename, config, logger)
	elif 'generate_all' == args.command:
		overlaymanager.resize(args.core, args.gamename, args.targetsizex, args.targetsizey, args.marginx, args.marginy, args.resizemode, args.backgroundcolor, 
			args.transparency, args.padding, config, logger)
		overlaymanager.generateCfg(args.core, args.gamename, args.transparency, args.padding, config, logger)
		overlaymanager.generateShader(args.core, args.gamename, config, logger)
		overlaymanager.generateOverlay(args.core, args.gamename, config, logger)
		overlaymanager.generateLayout(args.core, args.gamename, args.transparency, args.padding,config, logger)
	elif 'overlay_generate' == args.command:
		overlaymanager.generateOverlay(args.core, args.gamename, config, logger)
	elif 'layout_generate' == args.command:
		overlaymanager.generateLayout(args.core, args.gamename, args.transparency, args.padding,config, logger)
	elif 'bezel_resize' == args.command:
		overlaymanager.resize(args.core, args.gamename, args.targetsizex, args.targetsizey, args.marginx, args.marginy, args.resizemode, args.backgroundcolor, 
			args.transparency, args.padding, config, logger)
	else:
		logger.error('Command not supported')
		return -1
		
if __name__ == '__main__':
	setupLogging(logger)
	logger.debug("Program start")
	main()
	logger.debug("Program stop")
