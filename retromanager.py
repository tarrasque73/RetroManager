import os
import getopt
import sys
import configparser
import overlaymanager

config = []

def readConfig():
	if (not os.path.exists('config.ini')):
		print('ERROR: Missing configuration file: config.ini')
		return -1

	global config
	config = configparser.ConfigParser()
	config.read('config.ini')
	#print("config: ", config['overlaymanager'])

	if ('overlaymanager' not in config):
		print('ERROR: Missing configuration section: [overlaymanager]')
		return -1
	if ('realoverlaybasedir' not in config['overlaymanager']):
		print('ERROR: Missing configuration key: [overlaymanager] realoverlaybasedir')
		return -1
	
def setupUsage():
	import argparse
	parser = argparse.ArgumentParser(description="Library to generate and manipulate overlay image files and other configuration files for the RetroArch emulator frontend.")
	
	
	#parser.add_argument("command", help="Main command to execute", choices=['overlay_generate', 'config_generate', 'shader_generate', 'generate_all'])
	#parser.add_argument("core", help="The RetroArch core")
	#parser.add_argument("gamename", help="The MAME game name")

	#parser.add_argument("-tx", "--targetsizex", type=int, help="Target X size of the generated overlay")
	#parser.add_argument("-ty", "--targetsizey", type=int, help="Target Y size of the generated overlay")

	parent_parser = argparse.ArgumentParser(add_help=False)
	parent_parser.add_argument("core", help="The RetroArch core")
	parent_parser.add_argument("gamename", help="The MAME game name")
	
	subparsers = parser.add_subparsers(dest='command', title='commands', description='valid commands', help='add -h after the command name to display help about the command')
	
	parser_overlay_generate = subparsers.add_parser('overlay_generate', description="Generate overlay images and configuration file", help="Generate overlay files", parents=[parent_parser])
	#parser_overlay_generate.add_argument("core", help="The RetroArch core")
	#parser_overlay_generate.add_argument("gamename", help="The MAME game name")
	parser_overlay_generate.add_argument("-tx", "--targetsizex", type=int, default=0, help="target X size of the generated overlay")
	parser_overlay_generate.add_argument("-ty", "--targetsizey", type=int, default=0, help="target Y size of the generated overlay")

	parser_config_generate = subparsers.add_parser('config_generate', description="Generate RetroArch configuration files", help="Generate configuration files", parents=[parent_parser])
	#parser_config_generate.add_argument("core", help="The RetroArch core")
	#parser_config_generate.add_argument("gamename", help="The MAME game name")
	
	parser_shader_generate = subparsers.add_parser('shader_generate', description="Generate shader configuration files", help="Generate shader files", parents=[parent_parser])
	#parser_shader_generate.add_argument("core", help="The RetroArch core")
	#parser_shader_generate.add_argument("gamename", help="The MAME game name")

	parser_shader_generate = subparsers.add_parser('generate_all', description="Performs config_generate, overlay_generate, shader_generate", help="Generate all files", parents=[parent_parser])

	args = parser.parse_args()
	
	if not vars(args):
		parser.print_help()
		parser.exit(1)	
		
	return args

def main():
	args = setupUsage()
	print(args)
	readConfig()

	if 'config_generate' == args.command:
		overlaymanager.genCfg(args.core, args.gamename, config)
	elif 'overlay_generate' == args.command:
		overlaymanager.genOverlay(args.core, args.gamename, args.targetsizex, args.targetsizey, config)
	elif 'shader_generate' == args.command:
		readConfig()
		overlaymanager.genShader(args.core, args.gamename, config)
	elif 'generate_all' == args.command:
		overlaymanager.genCfg(args.core, args.gamename, config)
		overlaymanager.genOverlay(args.core, args.gamename, config)
		overlaymanager.genShader(args.core, args.gamename, config)
	else:
		print('Command not supported')
		return -1
		
if __name__ == '__main__':
	#print("Start program\n")
	main()
	#print("\nEnd program")