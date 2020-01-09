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

def getTemplate(filename, folder, default, logger):
	fullfilename = folder + filename
	fulldefaultname = folder + default
	if (os.path.exists(fullfilename)):
		logger.debug("Using specific template file: %s" % fullfilename)
		return fullfilename
	elif (os.path.exists(fulldefaultname)):
		logger.debug("Using default template file: %s" % fulldefaultname)
		return fulldefaultname
	else:
		logger.error("Missing configuration file: %s" % fulldefaultname)
		exit(-1)	

def writeLayoutCfg(gamename, layoutcfgfilepath, imagename, viewport_width, viewport_height, viewport_x, viewport_y, bezel_width, bezel_height, logger):
	layoutcfgfilename = gamename + ".lay"
	layoutcfgfilefullpath = layoutcfgfilepath  + layoutcfgfilename
	formats = {'imagename': imagename, 'viewport_height': viewport_height, 'viewport_width': viewport_width, 'viewport_x': viewport_x, 
		'viewport_y': viewport_y, 'bezel_width': bezel_width, 'bezel_height': bezel_height}
	template = getTemplate(gamename + ".lay", "templates\\layouts\\", "_default.lay", logger)
	writeConfig(layoutcfgfilefullpath, template, formats)
	#writeConfig(layoutcfgfilefullpath, "templates\\layouts\\template.lay", formats)
	logger.info("Layout configuration file %s written" % layoutcfgfilefullpath)

def writeOverlayCfg(gamename, overlaycfgfilepath, imagename, logger):
	overlaycfgfilename = gamename + ".cfg"
	overlaycfgfilefullpath = overlaycfgfilepath  + overlaycfgfilename
	formats = {'imagename': imagename}
	template = getTemplate(gamename + ".cfg", "templates\\overlays\\", "_default.cfg", logger)
	#writeConfig(overlaycfgfilefullpath, "templates\\overlays\\template.cfg", formats)
	writeConfig(overlaycfgfilefullpath, template, formats)
	logger.info("Overlay configuration file %s written" % overlaycfgfilefullpath)

def writeCore(gamename, corecfgfilepath, realoverlaybasedir, viewport_width, viewport_height, viewport_x, viewport_y, logger):
	corecfgfilename = gamename + ".cfg"
	corecfgfilefullpath = corecfgfilepath  + corecfgfilename
	formats = {'viewport_height': viewport_height, 'viewport_width': viewport_width, 'viewport_x': viewport_x, 
		'viewport_y': viewport_y, 'realoverlaybasedir': realoverlaybasedir, 'corecfgfilename': corecfgfilename}
	template = getTemplate(gamename + ".cfg", "templates\\config\\", "_default.cfg", logger)
	#writeConfig(corecfgfilefullpath, "templates\\config\\template.cfg", formats)
	writeConfig(corecfgfilefullpath, template, formats)
	logger.info("Core configuration file %s written" % corecfgfilefullpath)
	
def writeShader(gamename, shadercfgfilepath, logger):
	shadercfgfilename = gamename + ".cgp"
	shadercfgfilefullpath = shadercfgfilepath  + shadercfgfilename
	formats = {}
	template = getTemplate(gamename + ".cgp", "templates\\shaders\\", "_default.cgp", logger)
	#writeConfig(shadercfgfilefullpath, "templates\\shaders\\template.cgp", formats)
	writeConfig(shadercfgfilefullpath, template, formats)
	logger.info("Shader configuration file %s written" % shadercfgfilefullpath)
	
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
	
	logger.info("Game size: %d * %d, ratio %.10f" % (gamex, gamey, gamex / float(gamey)))
	logger.info("Target size: %d * %d, ratio %.10f (Multiplied X%d)" % (targetx, targety, gamer, z))
	cips = 4 / float(3)
	logger.info("4/3 = %.10f" % cips)

def ___getViewportAxisRange(axis, im, tt, padding, logger):
	if (axis == "x"):
		stop = im.size[0]
		fixed = im.size[1] / 2
	else:
		stop = im.size[1]
		fixed = im.size[0] / 2

	start = 0
	firsttransparent = 0
	firstcounter = 0
	
	logger.debug("Viewport scan on %s axis : fixed dimension at: %d" % (axis, fixed))
	for i in range (start, stop):
		if (axis == "x"):
			pix = im.getpixel((i, fixed))
		else:
			pix = im.getpixel((fixed, i))
			
		if pix[3] >= tt and firstcounter < padding:
			firsttransparent = 0
			lasttransparent = 0
			firstcounter = 0
		if pix[3] < tt and firsttransparent == 0 and firstcounter >= padding:
			firsttransparent = i
			logger.debug("Got first trasparent on %s axis at : %d" % (axis, firsttransparent))
		if pix[3] < tt and firsttransparent != 0:
			lasttransparent = i
		if pix[3] < tt:
			firstcounter = firstcounter +1
	logger.debug("Got last trasparent on %s axis at : %d" % (axis, lasttransparent))

	viewportsize = lasttransparent - firsttransparent

	logger.debug("Viewport scan on %s axis : %d to %d (size %d)" % (axis, firsttransparent, lasttransparent, viewportsize))
	
	return viewportsize, firsttransparent
	
def getViewportAxisRange(axis, im, tt, padding, logger):
	if (axis == "x"):
		stop = im.size[0]
		fixed = im.size[1] / 2
	else:
		stop = im.size[1]
		fixed = im.size[0] / 2

	start = 0
	firsttransparent = 0
	lasttransparent = stop
	firstcounter = 0
	
	logger.debug("Viewport scan on %s axis from %d to %d,  fixed dimension at: %d" % (axis, start, stop, fixed))
	for i in range (start, stop):
		if (axis == "x"):
			pix = im.getpixel((i, fixed))
		else:
			pix = im.getpixel((fixed, i))
			
		if pix[3] < tt and firsttransparent == 0:
			firsttransparent = i
			logger.debug("Got first trasparent on %s axis at : %d" % (axis, firsttransparent))
		if pix[3] >= tt and firsttransparent != 0 and lasttransparent == stop:
			lasttransparent = i-1
			logger.debug("Got last trasparent on %s axis at : %d" % (axis, lasttransparent))

	lasttransparent = lasttransparent - padding
	firsttransparent = firsttransparent + padding
	viewportsize = lasttransparent - firsttransparent

	logger.debug("Viewport scan on %s axis : %d to %d (size %d)" % (axis, firsttransparent, lasttransparent, viewportsize))
	
	return viewportsize, firsttransparent
	
def getViewportRange(im, tt, padding, logger):
	xsize, firstxtransparent = getViewportAxisRange("x", im, tt, padding, logger)
	ysize, firstytransparent = getViewportAxisRange("y", im, tt, padding, logger)
	
	return firstxtransparent, firstytransparent, xsize, ysize 

def resize(core, gamename, maxwidth, maxheight, marginx, marginy, customx, customy, mode, bc, tt, padding, config, logger):

	imagename = gamename + ".png"
	imagefilename = config['resize']['inputresizebasedir'] + imagename
	overlaydir = config['resize']['outputresizebasedir']
	os.makedirs(overlaydir, exist_ok=True)

	logger.info("Resizing image: %s with mode %s" % (imagefilename, mode))
	logger.debug('Max width / height: %s %s' % (maxwidth, maxheight))
	
	if (not os.path.exists(imagefilename)):
		logger.error('Missing image file: %s' % imagefilename)
		exit(-1)
		
	im = Image.open(imagefilename)
	logger.debug("Original image data: %s %s %s %s %s" % (im.format, im.size, im.mode, mode, im.getbands()))
	
	if (maxwidth == 0) :
		maxwidth = im.width
	if (maxheight == 0) :
		maxheight = im.height
		
	if (customx == 0) :
		customx = im.width
	if (customy == 0) :
		customy = im.height

	if (mode == 'custom') and (customx > maxwidth) :
		logger.error("Custom X viewport size %d must be smaller than X target size %d ." % (customx, maxwidth))
		return -1	
	if (mode == 'custom') and (customy > maxheight) :
		logger.error("Custom Y viewport size %s must be smaller than Y target size %d." % (customy, maxheight))
		return -1	
		
	if (maxwidth == im.width and maxheight == im.height and mode == 'outer') :
		logger.info("No resizing needed")
		copy(imagefilename, overlaydir + imagename)
	else:		
		#get size of the viewport of the original overlay
		viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im, tt, padding, logger)
		logger.info("Original viewport size: x %d y %d w %d h %d" % (viewport_x, viewport_y, viewport_width, viewport_height))	

		#sanity checks
		if (viewport_width < 1 or viewport_height < 1) :
			logger.error("No transparent viewport found.")
			return -1	
		
		#calculate target size and area to base the resize operation depending on mode
		if (mode == 'inner') :
			areax = viewport_width
			areay = viewport_height
			resizewidth = maxwidth - marginx
			resizeheight = maxheight - marginy
		elif (mode == 'outer') :
			areax = im.width
			areay = im.height
			resizewidth = maxwidth - marginx
			resizeheight = maxheight - marginy
		elif (mode == 'custom') :
			areax = viewport_width
			areay = viewport_height
			resizewidth = customx
			resizeheight = customy
		else :
			logger.error('Resize mode %s not supported' % mode)

		#calculate the actual new ratio, width and height for the resized image
		ratio = min(resizewidth/areax, resizeheight/areay)
		new_width = round(im.width  * ratio)
		new_height = round(im.height  * ratio)
		
		#resize the image
		newim = im.resize((new_width, new_height), Image.ANTIALIAS)
		logger.debug("Resized image data: %s %s %s %s" % (im.format, newim.size, newim.mode, newim.getbands()))
		#####newim.save(overlaydir + "resized_" + imagename, "PNG")

		#get size of the viewport of the resized overlay
		rviewport_x, rviewport_y, rviewport_width, rviewport_height = getViewportRange(newim, tt, padding, logger)
		logger.info("Resized viewport size: x %d y %d w %d h %d" % (rviewport_x, rviewport_y, rviewport_width, rviewport_height))
		
		#calculate offset for pasting the resized image and the mask, depending on resize mode
		if (mode == 'inner') :
			offsetx = round((maxwidth - rviewport_width) / 2 - rviewport_x)
			offsety = round((maxheight - rviewport_height) / 2 -rviewport_y)
		elif (mode == 'outer') :
			offsetx = round((maxwidth - new_width) / 2)
			offsety = round((maxheight - new_height) / 2)
		elif (mode == 'custom') :
			offsetx = round((maxwidth - rviewport_width) / 2 - rviewport_x)
			offsety = round((maxheight - rviewport_height) / 2 -rviewport_y)
		else :
			logger.error('Resize mode %s not supported' % mode)
		
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
		#####backim.save(overlaydir + "composite_" + imagename, "PNG")

		#save overlay
		backim.save(overlaydir + imagename, "PNG")
		logger.info("Resided bezel %s written" % (overlaydir + imagename))
	
def generateOverlay(core, gamename, config, logger):

	imagename = gamename + ".png"
	imagefilename = config['overlay']['inputoverlaybasedir'] + imagename
	overlaydir = config['overlay']['outputoverlaybasedir']
	os.makedirs(overlaydir, exist_ok=True)

	im = Image.open(imagefilename)
	logger.debug("Overlay image data: %s %s %s %s" % (im.format, im.size, im.mode, im.getbands()))

	#write overlay config file
	writeOverlayCfg(gamename, overlaydir, imagename, logger)
	
def generateLayout(core, gamename, tt, padding, config, logger):

	imagename = gamename + ".png"
	imagefilename = config['layout']['inputlayoutbasedir'] + imagename
	layoutdir = config['layout']['outputlayoutbasedir']
	os.makedirs(layoutdir, exist_ok=True)
	
	im = Image.open(imagefilename)
	logger.debug("Layout image data: %s %s %s %s" % (im.format, im.size, im.mode, im.getbands()))
	
	viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im, tt, padding, logger)

	#write layout config file
	writeLayoutCfg(gamename, layoutdir, imagename, viewport_width, viewport_height, viewport_x, viewport_y, im.width, im.height, logger)
	
def generateCfg(core, gamename, tt, padding, config, logger):
	imagename = gamename + ".png"
	imagefilename = config['config']['inputoverlaybasedir'] + imagename
	coredir = config['config']['outputcorebasedir'] + core + "\\"

	im = Image.open(imagefilename)
	logger.debug("Image data: %s %s %s %s" % (im.format, im.size, im.mode, im.getbands()))
	
	viewport_x, viewport_y, viewport_width, viewport_height = getViewportRange(im, tt, padding, logger)
	logger.info("Viewport: %s %s %s %s" % (viewport_x, viewport_y, viewport_width, viewport_height))
	
	#print("Test new viewport size: ", newxsize, newysize)
	
	if (viewport_width < 1 or viewport_height < 1) :
		logger.error("No transparent viewport found.")
		return -1
	
	viewport_r = viewport_height / float(viewport_width)		
	logger.debug("Viewport size: [%d * %d], ratio %.10f" % (viewport_width, viewport_height, viewport_r))

	realoverlaybasedir = config['general']['realoverlaybasedir']
	
	os.makedirs(coredir, exist_ok=True)	
	
	writeCore(gamename, coredir, realoverlaybasedir, viewport_width, viewport_height, viewport_x, viewport_y, logger)

def generateShader(core, gamename, config, logger):
	shaderdir = config['shader']['outputshaderbasedir'] + core + "\\"
	os.makedirs(shaderdir, exist_ok=True)
	writeShader(gamename, shaderdir, logger)
	
def copyOverlay(core, gamename, config):
	imagename = gamename + ".png"
	inputdir = config['general']['inputbasedir']
	overlaydir = config['general']['outputoverlaybasedir']
	os.makedirs(overlaydir, exist_ok=True)
	copy(inputdir + imagename, overlaydir + imagename)
	writeOverlay(gamename, overlaydir, imagename, logger)
