# photobooth
A Raspberry-Pi powered photobooth using gPhoto 2.

## RTIacquire branch 

This is a test branch which uses J. Cupitt's
[RTIacquire](http://github.com/jcupitt/rtiacquire) in order to improve
the FPS of previews from the camera. Usage:

    cd rtiacquire.orig
    python setup.py build
    sudo python setup.py install
    cd ..
    ./photobooth.sh

This is not neatly integrated yet. (See line 41 of camera.py).

Although this is already faster for previews than gphoto2cffi and
piggyphoto, it is not yet optimized. In particular, using PILLOW
Images seems to affect the speed. (Try ./rtitest.py to see the FPS
when using a pure pygame implementation.)
