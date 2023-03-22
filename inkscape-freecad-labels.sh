#!/usr/bin/env python

PYTHON=${HOME}/.FreeCAD/squashfs-root/usr/bin/python

export PYTHONPATH=${PYTHONPATH}:.FreeCAD/squashfs-root/usr/lib

${PYTHON} part-hack.py $@
