#!/bin/bash

cd $(dirname $0)	# Directory of this script

if [[ $1 == "set-time" ]]; then
  sudo python set-time.py
fi

python photobooth.py >>photobooth.log 2>>photobooth.err


