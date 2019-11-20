import os
import pathlib
from shutil import copy
from PIL import Image, ImageDraw

def writeConfig(outputfile, templatefile, formats):
	of = open(outputfile, 'wt', encoding='utf-8')
	with open(templatefile) as tf:
		line = tf.readline()
		while line:
			of.write(line.format(**formats))
			line = tf.readline()
	
	of.close

def writeOverlayCfg(gamename, overlaycfgfilepath, imagename):
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

def resize(core, gamename, maxwidth, maxheight, marginx, marginy, mode, bc, config):
	imagename = gamename + ".png"
	imagefilename = config['overlay']['inputoverlaybasedir'] + imagename
	overlaydir = config['general']['outputoverlaybasedir']
	os.makedirs(overlaydir, exist_ok=True)

	print("Resizing image: ", imagefilename)
	
	print('Max width / height', maxwidth, maxheight)
	
	im = Image.open(imagefilename)
	print("Original image data: ", im.format, im.size, im.mode, mode, im.getbands())
	
	if (maxwidth == 0) :
		maxwidth = im.width
	if (maxheight == 0) :
		maxheight = im.height
		
	if (maxwidth == im.width and maxheight == im.height and mode == 'outer') :
		print("No resizing needed")
		copy(imagefilename, overlaydir + imagename)
	else:		
		#get size of the viewport of the original overlay
		viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im)
		print("Original viewport size: x %d y %d w %d h %d" % (viewport_x, viewport_y, viewport_width, viewport_height))	

		#sanity checks
		if (viewport_width < 1 or viewport_height < 1) :
			print("ERROR: No transparent viewport found.")
			return -1	
		
		#calculate resized image target size accounting for margins
		resizewidth = maxwidth - marginx
		resizeheight = maxheight - marginy
		
		#calculate area to base the resize operation depending on mode (inner, outer)
		if (mode == 'inner') :
			areax = viewport_width
			areay = viewport_height
		else:
			areax = im.width
			areay = im.height

		#calculate the actual new ratio, width and height for the resized image
		ratio = min(resizewidth/areax, resizeheight/areay)
		new_width = round(im.width  * ratio)
		new_height = round(im.height  * ratio)
		
		#resize the image
		newim = im.resize((new_width, new_height), Image.ANTIALIAS)
		print("Resized image data:", im.format, newim.size, newim.mode, newim.getbands())
		#####newim.save(overlaydir + "resized_" + imagename, "PNG")

		#get size of the viewport of the resized overlay
		rviewport_x, rviewport_y, rviewport_width, rviewport_height = getViewportRange(newim)
		print("Resized viewport size: x %d y %d w %d h %d" % (rviewport_x, rviewport_y, rviewport_width, rviewport_height))
		
		#calculate offset for pasting the resized image and the mask, depending on resize mode
		if (mode == 'inner') :
			offsetx = round((maxwidth - rviewport_width) / 2 - rviewport_x)
			offsety = round((maxheight - rviewport_height) / 2 -rviewport_y)
		else:
			offsetx = round((maxwidth - new_width) / 2)
			offsety = round((maxheight - new_height) / 2)
		
		#create background image
		backim = Image.new("RGBA", (maxwidth, maxheight), "#" + bc)
		#####backim.save(overlaydir + "bkg_" + imagename, "PNG")

		#create transparency mask
		newmask = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 0))
		
		#paste mask over background
		backim.paste(newmask, (offsetx, offsety))
		#####backim.save(overlaydir + "mask_" + imagename, "PNG")
		
		#paste resized image over backgound and mask
		backim.paste(newim, (offsetx, offsety))
		#####backim.save(overlaydir + "final_" + imagename, "PNG")

		#save overlay
		backim.save(overlaydir + imagename, "PNG")

	#write overlay config file
	writeOverlayCfg(gamename, overlaydir, imagename)
	

def genCfg(core, gamename, config):
	imagename = gamename + ".png"
	imagefilename = config['config']['inputoverlaybasedir'] + imagename

	print("Checking image: ", imagename)
	print(imagefilename)
	
	im = Image.open(imagefilename)
	print("Image data: ", im.format, im.size, im.mode, im.getbands())
	
	viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im)
	
	#print("Test new viewport size: ", newxsize, newysize)
	
	if (viewport_width == 0 or viewport_height == 0) :
		print("No transparent viewport found.")
		return -1
	
	viewport_r = viewport_height / float(viewport_width)		
	print("Viewport size: [%d * %d], ratio %.10f" % (viewport_width, viewport_height, viewport_r))
	print("")		

	coredir = config['general']['outputcorebasedir'] + core + "\\"
	realoverlaybasedir = config['general']['realoverlaybasedir']
	
	os.makedirs(coredir, exist_ok=True)	
	
	writeCore(gamename, coredir, realoverlaybasedir, viewport_width, viewport_height, viewport_x, viewport_y)

def genShader(core, gamename, config):
	shaderdir = config['general']['outputshaderbasedir'] + core + "\\"
	os.makedirs(shaderdir, exist_ok=True)
	writeShader(gamename, shaderdir)
	
def copyOverlay(core, gamename, config):
	imagename = gamename + ".png"
	inputdir = config['general']['inputbasedir']
	overlaydir = config['general']['outputoverlaybasedir']
	os.makedirs(overlaydir, exist_ok=True)
	copy(inputdir + imagename, overlaydir + imagename)
	writeOverlay(gamename, overlaydir, imagename)
	
