#!/usr/bin/python

# Let's see if we can use  rtiacquire's interface to gphoto2 library
# which is much faster than gphoto2cffi for reading previews.

from rtiacquire import decompress, camera as gp
import os, ctypes
import pygame
from cStringIO import StringIO
import cv2, numpy

# get the directory this source is in
source_dir = os.path.dirname(__file__)

# get the directory the dejpeg.so library is in
source_dir = source_dir + "/rtiacquire.orig/build/lib.linux-armv7l-2.7/rtiacquire"

# Load library
decompress = ctypes.CDLL(os.path.join(source_dir, 'dejpeg.so'))

class ByteImage(ctypes.Structure):
    _fields_ = [('width', ctypes.c_int),
                ('height', ctypes.c_int),
                ('pixels', ctypes.c_void_p)]


pygame.init()
pygame.display.set_caption('RTItest')
screen=pygame.display.set_mode((0,0), pygame.FULLSCREEN)            
i = pygame.display.Info()
size = (i.current_w, i.current_h)
screen.fill((0,0,0))
pygame.display.update()




cap=gp.Camera()


#cap.set_canon_capture(1)        # Should be harmless for non-canon.

b = ByteImage()
from time import time
t=time()

frames=100
tries=0
experiment="opencv"

for i in range(frames):
    data=None
    while data==None:
        tries=tries+1
        (data, length) = cap.preview()

    if "decompress" in experiment:
        # This uses the CDLL decompress which I'd prefer to avoid
        decompress.decompress(data, length, ctypes.byref(b))
        string = ctypes.string_at(b.pixels, b.width * b.height * 3)
        image=pygame.image.frombuffer(string, (b.width,b.height), "RGB")
    elif "stringio" in experiment:
        # This works, but is slightly slower
        jpegstring = ctypes.string_at(data, length.value)
        jpegio = StringIO(jpegstring)
        image=pygame.image.load(jpegio)
    elif "opencv" in experiment:
        # This works swiftly. Only downside is relying on opencv, numpy.
        jpegstring = ctypes.string_at(data, length.value)
        nparray = numpy.fromstring(jpegstring, numpy.uint8)
        decimage = cv2.imdecode(nparray, 1)
        f=cv2.cvtColor(decimage,cv2.COLOR_BGR2RGB)
        f=numpy.rot90(f)        # OpenCV swaps rows and columns
        image = pygame.surfarray.make_surface(f)
    elif "numpy" in experiment:
        # I can write directly to a numpy array. Uglier code and
        # no speed benefit over opencv + string_at.
        buffer_from_memory = ctypes.pythonapi.PyBuffer_FromMemory
        buffer_from_memory.restype = ctypes.py_object
        buf = buffer_from_memory(data, length.value)
        nparray = numpy.frombuffer(buf, numpy.uint8)
        decimage = cv2.imdecode(nparray, 1)
        f=cv2.cvtColor(decimage,cv2.COLOR_BGR2RGB)
        f=numpy.rot90(f)        # OpenCV swaps rows and columns
        image = pygame.surfarray.make_surface(f)

    screen.blit(image, (0,0))
    pygame.display.update()
print ("%d reads for %d frames\n" % (tries,frames))
print ("\nFPS: %f\n" % (frames/(time()-t)))

#cap.capture_to_file("foo")      # Appends ".jpg" to filename automatically

cap.release()

