#!/bin/sh -x

cwd=`pwd`
export PYTHONPATH=$cwd/../../../src:$PYTHONPATH

ncpu=`cat /proc/cpuinfo | grep processor | wc -l`

python3 thread_test.py
if test $? -ne 0; then exit 1; fi

rm -rf obj_dir __pycache__
