import os
import pathlib
from shutil import copy
from PIL import Image

def writeConfig(outputfile, templatefile, formats):
	of = open(outputfile, 'wt', encoding='utf-8')
	with open(templatefile) as tf:
		line = tf.readline()
		while line:
			of.write(line.format(**formats))
			line = tf.readline()
	
	of.close

def writeOverlay(gamename, overlaycfgfilepath, imagename):
	overlaycfgfilename = gamename + ".cfg"
	overlaycfgfilefullpath = overlaycfgfilepath  + overlaycfgfilename
	formats = {'imagename': imagename}
	writeConfig(overlaycfgfilefullpath, "templates\\layouts\\template.cfg", formats)
	print("Overlay configuration file %s written" % overlaycfgfilefullpath)

def writeCore(gamename, corecfgfilepath, realoverlaybasedir, viewport_width, viewport_height, viewport_x, viewport_y):
	corecfgfilename = gamename + ".cfg"
	corecfgfilefullpath = corecfgfilepath  + corecfgfilename
	formats = {'viewport_height': viewport_height, 'viewport_width': viewport_width, 'viewport_x': viewport_x, 
		'viewport_y': viewport_y, 'realoverlaybasedir': realoverlaybasedir, 'corecfgfilename': corecfgfilename}
	writeConfig(corecfgfilefullpath, "templates\\config\\template.cfg", formats)
	print("Core configuration file %s written" % corecfgfilefullpath)
	
def writeShader(gamename, shadercfgfilepath):
	shadercfgfilename = gamename + ".cgp"
	shadercfgfilefullpath = shadercfgfilepath  + shadercfgfilename
	formats = {}
	writeConfig(shadercfgfilefullpath, "templates\\shaders\\template.cgp", formats)
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
	
def getViewportAxisRange(axis, im):
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
	
def getViewportRange(im):
	xsize, firstxtransparent = getViewportAxisRange("x", im)
	ysize, firstytransparent = getViewportAxisRange("y", im)
	
	return firstxtransparent, firstytransparent, xsize, ysize 

def genCfg(core, gamename, config):
	imagename = gamename + ".png"
	imagefilename = config['overlaymanager']['inputbasedir'] + imagename
	transparency = 200
	margin = 3

	print("Checking image: ", imagename)
	print(imagefilename)
	im = Image.open(imagefilename)
	print("Image data: ", im.format, im.size, im.mode, im.getbands())
	print("")
	
	viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im)
	
	#print("Test new viewport size: ", newxsize, newysize)
	
	if (viewport_width == 0 or viewport_height == 0) :
		print("No transparent viewport found.")
		return -1
	
	viewport_r = viewport_height / float(viewport_width)		
	print("Viewport size: [%d * %d], ratio %.10f" % (viewport_width, viewport_height, viewport_r))
	print("")		

	coredir = config['overlaymanager']['outputcorebasedir'] + core + "\\"
	realoverlaybasedir = config['overlaymanager']['realoverlaybasedir']
	
	os.makedirs(coredir, exist_ok=True)	
	
	writeCore(gamename, coredir, realoverlaybasedir, viewport_width, viewport_height, viewport_x, viewport_y)

def genShader(core, gamename, config):
	shaderdir = config['overlaymanager']['outputshaderbasedir'] + core + "\\"
	os.makedirs(shaderdir, exist_ok=True)
	writeShader(gamename, shaderdir)
	
def genOverlay(core, gamename, config):
	imagename = gamename + ".png"
	inputdir = config['overlaymanager']['inputbasedir']
	overlaydir = config['overlaymanager']['outputoverlaybasedir']
	os.makedirs(overlaydir, exist_ok=True)
	copy(inputdir + imagename, overlaydir + imagename)
	writeOverlay(gamename, overlaydir, imagename)
	
