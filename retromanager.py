import os
import getopt
import sys
import configparser
import overlaymanager

config = []

def usage():
	print("Usage: python %s <command> <arguments>" % sys.argv[0])
	print("<command>: accepted values are currently only: help and gencfg")
	print("<arguments>: Argument list depending on <command>")
	print("")
	print("Command listing and supported arguments:")
	print("")
	print("help: Prints this help info.")
	print("Syntax: python %s help" % sys.argv[0])
	print("")
	print("gencfg: Scans input folder for image overlays, detects the transparent viewport")
	print("        and generates the corrsponding config files.")
	print("Syntax: python %s gencfg <core> <gamename>" % sys.argv[0])
	print("<core>: The Retroarch core you want the config files generated for.")
	print("        Used to create the output path where to create the output files.")
	print("        Remember to use quotes around the core name if it contains spaces.")
	print("<gamename>: The MAME core name of the game.")
	print("        Input folders will be scanned for *.png overlay images matching the gamename")
	print("        and output files will be named according to it.")
	print("Example: python %s gencfg \"MAME 2003-Plus\" pacman" % sys.argv[0])
	
def readConfig():
	if (not os.path.exists('config.ini')):
		print('ERROR: Missing configuration file: config.ini')
		return -1

	global config
	config = configparser.ConfigParser()
	config.read('config.ini')
	print("config: ", config['overlaymanager'])

	if ('overlaymanager' not in config):
		print('ERROR: Missing configuration section: [overlaymanager]')
		return -1
	if ('realoverlaybasedir' not in config['overlaymanager']):
		print('ERROR: Missing configuration key: [overlaymanager] realoverlaybasedir')
		return -1
	
def main():
	argv = sys.argv[1:]			
	#try:
	#	opts, args = getopt.getopt(argv,"-h")
	#except getopt.GetoptError:
	#	print("Usage: %s <command> <core> <arguments>" % sys.argv[0])
	#	sys.exit(2)

	#print("Arguments: [" + ", ".join(argv) + "]")
	#print("")

	if (len(sys.argv) == 1):
		usage()
	elif ('help' == sys.argv[1]):
		usage()
	elif ('checkconfig' == sys.argv[1]):
		readConfig()
	elif 'gencfg' == sys.argv[1]:
		readConfig()
		core = sys.argv[2]
		gamename = sys.argv[3]
		overlaymanager.gencfg(core, gamename, config)
	else:
		print('Function not supported')
		return -1
		
if __name__ == '__main__':
	#print("Start program\n")
	main()
	#print("\nEnd program")