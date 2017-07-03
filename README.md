# photobooth
A Raspberry-Pi powered photobooth using gPhoto 2.

## RTIacquire branch 

This was a test branch which used J. Cupitt's
[RTIacquire](http://github.com/jcupitt/rtiacquire) in order to improve
the FPS of previews from the camera.

I have abandoned this as it turns out that piggyphoto, despite having
to write to the filesystem, is just as fast as rtiacquire. The slow
preview framerate appears to be a bug exclusive to gphoto2-cffi.

###Usage:

    cd rtiacquire.orig
    python setup.py build
    sudo python setup.py install
    cd ..
    ./photobooth.sh

This is not neatly integrated. (See line 41 of camera.py).

Although this is already faster for previews than gphoto2cffi, it is
not yet optimized. In particular, using PILLOW Images seems to affect
the speed. (Try ./rtitest.py to see the FPS when using a pure pygame
implementation.)
