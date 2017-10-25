#!/usr/bin/env python
# Created by br@re-web.eu, 2015

# TODO: This really ought to be a single class with subclasses for
# each backend (opencv, gphoto-cffi, piggyphoto, gphoto cmdline).

import os
import subprocess
import pygame
import numpy
from PIL import Image, ImageDraw, ImageFont


# Temp directory for storing pictures
if os.access("/dev/shm", os.W_OK):
	tmp_dir = "/dev/shm/"	   # Don't abuse Raspberry Pi SD card, if possible
else:
	tmp_dir = "/tmp/"


cv_enabled = False
pi_enabled = False
gphoto2cffi_enabled = False
piggyphoto_enabled = False

try:
	import cv2 as cv
	cv_enabled = True
	print('OpenCV available')
except ImportError:
	pass

try:
	from picamera.array import PiRGBArray
	from picamera import PiCamera
	from picamera import PiCameraError
	from picamera import PiCameraCircularIO
	from picamera import PiVideoFrameType
	from picamera import PiResolution
	pi_enabled = True
	print('PiCamera available')
except ImportError:
	pass

if not gphoto2cffi_enabled:
	try:
		import piggyphoto as gp
		gpExcept = gp.libgphoto2error
		piggyphoto_enabled = True
		print('Piggyphoto available')
	except ImportError:
		pass

class CameraException(Exception):
	"""Custom exception class to handle camera class errors"""
	def __init__(self, message, recoverable=False):
		self.message = message
		self.recoverable = recoverable


class Camera_pi:
	def __init__(self, resolution=(3104,2464), preview_resolution=(620,360), camera_rotate=False):
		if resolution[0]>0 and resolution[1]>0:
			self.resolution = resolution   # Requested camera resolution
		else:
			self.resolution = (3104,2464) # Just use highest resolution possible
		self.rotate = camera_rotate		# Is camera on its side?
		self.preview_message = None
		self.preview_resolution = preview_resolution;

		global pi_enabled
		if pi_enabled:
			try:
				self.camera = PiCamera(resolution=self.resolution)
				rawCapture = PiRGBArray(self.camera)
				self.camera.capture(rawCapture, format="bgr")
				image = rawCapture.array
			except PiCameraError:
				print "Warning: Failed to open camera using OpenCV"
				pi_enabled=False
				return
			print "Connecting to camera using opencv"
			self.camera.resolution = self.resolution

	def reinit(self):
		'''Close and reopen the video device.
		This is mainly for debugging video capture problems.
		'''
		self.camera.close()
		self.camera = PiCamera(resolution=PiResolution(self.resolution))

	def set_rotate(self, camera_rotate):
		self.rotate = camera_rotate

	def get_rotate(self):
		return self.rotate

	def has_preview(self):
		return False

	def take_preview(self, filename=tmp_dir + "preview.jpg"):
		self.take_picture(filename)

	def get_preview_array(self, max_size=None):
		print("get preview array")
		"""Get a quick preview from the camera and return it as a 2D array
		suitable for quick display using pygame.surfarray.blit_array().

		If a maximum size -- (w,h) -- is passed in, the returned image
		will be quickly decimated using numpy to be at most that large.
		"""

		global pi_enabled
		if not pi_enabled:
			pi_enabled=True
			self.__init__()	 # Try again to open the camera (e.g, just plugged in)
			if not pi_enabled:  # Still failed?
				raise CameraException("OpenCV: No camera found!")

		# Grab a camera frame
		try:
			self.camera.resolution=(640,480)
			rawCapture = PiRGBArray(self.camera)
			self.camera.capture(rawCapture, format="bgr")
			f = rawCapture.array
			self.camera.resolution=self.resolution
		except PiCameraError:
			pi_enabled=False
			raise CameraException("Error capturing frame using piCamera 1!")

		# Optionally reduce frame size by decimation (nearest neighbor)
		if max_size:
			(max_w, max_h) = map(int, max_size)
			(h, w) = (len(f), len(f[0]) ) # Note OpenCV swaps rows and columns
			w_factor = (w/max_w) + (1 if (w%max_w) else 0)
			h_factor = (h/max_h) + (1 if (h%max_h) else 0)
			scaling_factor = max( (w_factor, h_factor) )
			f=f[::scaling_factor, ::scaling_factor]

		# Convert from OpenCV format to Surfarray
		f=cv.cvtColor(f,cv.COLOR_BGR2RGB)
		f=numpy.rot90(f) # OpenCV swaps rows and columns

		return f

	def start_preview(self):
		self.camera.resolution = self.preview_resolution
		self.camera.start_preview()

	def stop_preview(self):
		self.clean_message()
		self.camera.stop_preview()

	def clean_message(self):
		if self.preview_message:
			self.camera.remove_overlay(self.preview_message);
			self.preview_message = None;

	def show_message(self, message, message_size, text_size):
		self.clean_message()
		img = Image.new("RGBA", message_size);
		draw = ImageDraw.Draw(img);
		draw.font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", text_size);
		w, h = draw.textsize(message);
		draw.text(((message_size[0]-w)/2, (message_size[1]-h)/2), message, (255, 255, 255));
		overlay = self.camera.add_overlay(img.tobytes(), size=img.size);
		overlay.layer = 3;
		self.preview_message = overlay;

	def take_picture(self, filename=tmp_dir+"picture.jpg"):
		global pi_enabled
		if pi_enabled:
			try:
				self.camera.resolution = self.resolution
				rawCapture = PiRGBArray(self.camera)
				self.camera.capture(rawCapture, format="bgr")
				frame = rawCapture.array
			except PiCameraError:
				pi_enabled=False
				raise CameraException("Error capturing frame using piCamera 2!")

			if self.rotate:
				frame=numpy.rot90(frame)
			cv.imwrite(filename, frame)
			return filename
		else:
			 raise CameraException("OpenCV not available!")

	def set_idle(self):
		pass

