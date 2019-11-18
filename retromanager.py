import os
import getopt
import sys
import configparser
import overlaymanager

config = []

def usage():
	print("Usage: python %s <command> <arguments>" % sys.argv[0])
	print("  <command>: accepted values are currently:")
	print("        help, config_generate, overlay_generate, shader_generate, generate_all")
	print("  <arguments>: Argument list depending on <command>")
	print("")
	print("Command listing and supported arguments:")
	print("")
	print("help: Prints this help info.")
	print("Syntax: python %s help" % sys.argv[0])
	print("")
	print("config_generate: Scans input folder for image overlays, detects the transparent viewport")
	print("        and generates the corresponding core config files, according to the template.")
	print("Syntax: python %s config_generate <core> <gamename>" % sys.argv[0])
	print("  <core>: The Retroarch core you want the config files generated for.")
	print("        Used to create the output path where to create the output files.")
	print("        Remember to use quotes around the core name if it contains spaces.")
	print("  <gamename>: The MAME core name of the game.")
	print("        Input folders will be scanned for *.png overlay images matching the gamename")
	print("        and output files will be named according to it.")
	print("Example: python %s config_generate \"MAME 2016\" pacman" % sys.argv[0])
	print("")
	print("overlay_generate: Scans input folder for image overlays, copies them to output directory")
	print("        and generates the corresponding layout config files, according to the template.")
	print("Syntax: python %s overlay_generate <core> <gamename>" % sys.argv[0])
	print("  <core>: The Retroarch core you want the config files generated for.")
	print("        Used to create the output path where to create the output files.")
	print("        Remember to use quotes around the core name if it contains spaces.")
	print("  <gamename>: The MAME core name of the game.")
	print("        Input folders will be scanned for *.png overlay images matching the gamename")
	print("        and output files will be named according to it.")
	print("Example: python %s overlay_generate \"MAME 2016\" pacman" % sys.argv[0])
	print("")
	print("shader_generate: Generates the shader preset config files, according to the template.")
	print("Syntax: python %s shader_generate <core> <gamename>" % sys.argv[0])
	print("  <core>: The Retroarch core you want the config files generated for.")
	print("        Used to create the output path where to create the output files.")
	print("        Remember to use quotes around the core name if it contains spaces.")
	print("  <gamename>: The MAME core name of the game.")
	print("        Input folders will be scanned for *.png overlay images matching the gamename")
	print("        and output files will be named according to it.")
	print("Example: python %s gen_shader \"MAME 2016\" pacman" % sys.argv[0])
	print("")
	print("generate_all: performs commands config_generate, overlay_generate and shader_generate with the supplied arguments.")
	print("Syntax: python %s generate_all <core> <gamename>" % sys.argv[0])
	
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
	
def main():
	argv = sys.argv[1:]			

	if (len(sys.argv) == 1):
		usage()
	elif ('help' == sys.argv[1]):
		usage()
	elif ('check_config' == sys.argv[1]):
		readConfig()
	elif 'config_generate' == sys.argv[1]:
		readConfig()
		core = sys.argv[2]
		gamename = sys.argv[3]
		overlaymanager.genCfg(core, gamename, config)
	elif 'overlay_generate' == sys.argv[1]:
		readConfig()
		core = sys.argv[2]
		gamename = sys.argv[3]
		overlaymanager.genOverlay(core, gamename, config)
	elif 'shader_generate' == sys.argv[1]:
		readConfig()
		core = sys.argv[2]
		gamename = sys.argv[3]
		overlaymanager.genShader(core, gamename, config)
	elif 'generate_all' == sys.argv[1]:
		readConfig()
		core = sys.argv[2]
		gamename = sys.argv[3]
		overlaymanager.genCfg(core, gamename, config)
		overlaymanager.genOverlay(core, gamename, config)
		overlaymanager.genShader(core, gamename, config)
	else:
		print('Function not supported')
		return -1
		
if __name__ == '__main__':
	#print("Start program\n")
	main()
	#print("\nEnd program")