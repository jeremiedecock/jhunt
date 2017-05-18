#!/bin/sh

# MACPORTS DEPENDENCIES:
# - gobject-introspection
# - py-gobject3
# - py27-gobject
# - py27-gobject3
# - py35-gobject3

MACPORTSPYTHONPATH=/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5
MACPORTSPYTHONPATH=$MACPORTSPYTHONPATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/plat-darwin
MACPORTSPYTHONPATH=$MACPORTSPYTHONPATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/lib-dynload
MACPORTSPYTHONPATH=$MACPORTSPYTHONPATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages

ANACONDAPYTHONPATH=~/anaconda/lib/python3.5
ANACONDAPYTHONPATH=$ANACONDAPYTHONPATH:~/anaconda/lib/python3.5/plat-darwin
ANACONDAPYTHONPATH=$ANACONDAPYTHONPATH:~/anaconda/lib/python3.5/lib-dynload
ANACONDAPYTHONPATH=$ANACONDAPYTHONPATH:~/anaconda/lib/python3.5/site-packages

# Run with MacPorts ###########################################################

#export PYTHONPATH=../../:$PYTHONPATH
#export PYTHONPATH=.:$PYTHONPATH
#
#/opt/local/bin/python3.5 ./jobmanager/job_advert_manager.py

# Run with Anaconda ###########################################################

#export PYTHONPATH=/opt/local/lib/girepository-1.0:$PYTHONPATH
#export PYTHONPATH=/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/gi:$PYTHONPATH

# Workaround:
# - GTK3 only works with MacPorts Python version (GTK3 is not available in Anaconda)
# - Some other packages only work with Anaconda Python version
# Thus:
# - Set both paths but give Anaconda a higher priority

export PYTHONPATH=$MACPORTSPYTHONPATH:$PYTHONPATH
export PYTHONPATH=$ANACONDAPYTHONPATH:$PYTHONPATH
export PYTHONPATH=.:$PYTHONPATH

python3 $(dirname "$0")/jobmanager/job_advert_manager.py
