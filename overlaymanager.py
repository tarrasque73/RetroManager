import sys
import getopt
import os
import pathlib
import configparser
from shutil import copy
from PIL import Image

config = []

def writeOverlay(gamename, overlaycfgfilepath, imagename):
	overlaycfgfilename = gamename + ".cfg"
	overlaycfgfilefullpath = overlaycfgfilepath  + overlaycfgfilename
	
	overlaycfgf = open(overlaycfgfilefullpath, 'wt', encoding='utf-8')
	overlaycfgf.write('overlays = 1\n')
	overlaycfgf.write('overlay0_overlay = %s\n' % imagename)
	overlaycfgf.write('overlay0_full_screen = true\n')
	overlaycfgf.write('overlay0_descs = 0')	
	overlaycfgf.close
	
	####################overlaytemplatef = open("templates\\layouts\\template.cfg", 'r', encoding='utf-8')
	with open("templates\\layouts\\template.cfg") as overlaytemplatef:
		line = overlaytemplatef.readline()
		while line:
			print("TEST: ", line.format(imagename=imagename))
			line = overlaytemplatef.readline()
	
	print("Overlay configuration file %s written" % overlaycfgfilefullpath)

def writeCore(gamename, corecfgfilepath, realoverlaybasedir, xsize, ysize, firstxtransparent, firstytransparent):
	corecfgfilename = gamename + ".cfg"
	corecfgfilefullpath = corecfgfilepath  + corecfgfilename
	
	corecfgf = open(corecfgfilefullpath, 'wt', encoding='utf-8')
	corecfgf.write('aspect_ratio_index = "23"\n')
	corecfgf.write('custom_viewport_height = "%d"\n' % ysize)
	corecfgf.write('custom_viewport_width = "%d"\n' % xsize)
	corecfgf.write('custom_viewport_x = "%d"\n' % firstxtransparent)
	corecfgf.write('custom_viewport_y = "%d"\n' % firstytransparent)
	corecfgf.write('input_overlay = \"%s%s\"\n' % (realoverlaybasedir, corecfgfilename))
	corecfgf.write('input_overlay_enable = "true"\n')
	corecfgf.write('input_overlay_hide_in_menu = "false"\n')
	corecfgf.write('video_shader_enable = "true"\n')
	corecfgf.write('video_fullscreen = "true"\n')
	corecfgf.close
	
	print("Core configuration file %s written" % corecfgfilefullpath)

def writeShader(gamename, shadercfgfilepath):
	shadercfgfilename = gamename + ".cgp"
	shadercfgfilefullpath = shadercfgfilepath  + shadercfgfilename
	
	shadercfgf = open(shadercfgfilefullpath, 'wt', encoding='utf-8')
	shadercfgf.write('#reference "..\..\shaders_cg\crt\crt-geom.cgp')
	shadercfgf.close
	
	print("Shader configuration file %s written" % shadercfgfilefullpath)


def upscale():
	gamex = 320
	gamey = 224
	
	screenx = 1920
	screeny = 1080
	z = 0
	tx = 0
	ty = 0
	
	while (z < 10):
		tx = gamex * z
		ty = gamey * z
		if ((tx > screenx) or (ty > screeny)):
			z = z - 1
			break
		z = z + 1
	
	targetx = gamex * z
	targety = gamey * z
	gamer = targetx / float(targety)
	
	print("Game size: %d * %d, ratio %.10f" % (gamex, gamey, gamex / float(gamey)))
	print("Target size: %d * %d, ratio %.10f (Multiplied X%d)" % (targetx, targety, gamer, z))
	cips = 4 / float(3)
	print("4/3 = %.10f" % cips)
	
def getViewportRange(axis, im):
	transparency = 200
	margin = 3

	if (axis == "x"):
		stop = im.size[0]
		fixed = im.size[1] / 2
	else:
		stop = im.size[1]
		fixed = im.size[0] / 2

	start = 0
	firsttransparent = 0
	firstcounter = 0
	
	for i in range (start, stop):
		if (axis == "x"):
			pix = im.getpixel((i, fixed))
		else:
			pix = im.getpixel((fixed, i))
			
		if pix[3] >= transparency and firstcounter < margin:
			firsttransparent = 0
			lasttransparent = 0
			firstcounter = 0
		if pix[3] < transparency and firsttransparent == 0 and firstcounter >= margin:
			firsttransparent = i
		if pix[3] < transparency and firsttransparent != 0:
			lasttransparent = i
		if pix[3] < transparency:
			firstcounter = firstcounter +1

	viewportsize = lasttransparent - firsttransparent

	print("First %s transparent pixel: %d" % (axis, firsttransparent))
	print("Last %s transparent pixel: %d" % (axis, lasttransparent))
	
	return viewportsize, firsttransparent
	
def gencfg(core, gamename):
	imagename = gamename + ".png"
	imagefilename = config['overlaymanager']['inputbasedir'] + imagename
	transparency = 200
	margin = 3

	print("Checking image: ", imagename)
	print(imagefilename)
	im = Image.open(imagefilename)
	print("Image data: ", im.format, im.size, im.mode, im.getbands())
	print("")
	
	xsize, firstxtransparent = getViewportRange("x", im)
	ysize, firstytransparent = getViewportRange("y", im)
	
	#print("Test new viewport size: ", newxsize, newysize)
	
	if (xsize == 0 or ysize == 0) :
		print("No transparent viewport found.")
		return -1
	
	viewportr = ysize / float(xsize)		
	print("Viewport size: [%d * %d], ratio %.10f" % (xsize, ysize, viewportr))
	print("")		

	inputdir = config['overlaymanager']['inputbasedir']
	overlaydir = config['overlaymanager']['outputoverlaybasedir']
	coredir = config['overlaymanager']['outputcorebasedir'] + core + "\\"
	shaderdir = config['overlaymanager']['outputshaderbasedir'] + core + "\\"
	
	os.makedirs(overlaydir, exist_ok=True)
	os.makedirs(coredir, exist_ok=True)
	os.makedirs(shaderdir, exist_ok=True)
	
	overlayfilename = imagename
	copy(inputdir + imagename, overlaydir + overlayfilename)
	
	realoverlaybasedir = config['overlaymanager']['realoverlaybasedir']
	
	writeOverlay(gamename, overlaydir, imagename)
	writeCore(gamename, coredir, realoverlaybasedir, xsize, ysize, firstxtransparent, firstytransparent)
	writeShader(gamename, shaderdir)

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
		gencfg(core, gamename)
	else:
		print('Function not supported')
		return -1
		
if __name__ == '__main__':
	#print("Start program\n")
	main()
	#print("\nEnd program")
