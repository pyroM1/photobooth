#!/usr/bin/python

# Let's see if we can use the gphoto2 library builtin to rtiacquire
# which is much faster for reading gphoto2 previews.

from rtiacquire import decompress, camera as gp
import ctypes, os
import pygame
from PIL  import Image

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
for i in range(frames):
    data=None
    while data==None:
        tries=tries+1
        (data, length) = cap.preview()
    decompress.decompress(data, length, ctypes.byref(b))

    string = ctypes.string_at(b.pixels, b.width * b.height * 3)
    image=pygame.image.frombuffer(string, (b.width,b.height), "RGB")
    screen.blit(image, (0,0))
    pygame.display.update()
print ("%d reads for %d frames\n" % (tries,frames))
print ("\nFPS: %f\n" % (frames/(time()-t)))

#cap.capture_to_file("foo")      # Appends ".jpg" to filename automatically

cap.release()

