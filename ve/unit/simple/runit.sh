#!/bin/sh -x

# TODO: auto-set PYTHONPATH (?)


python3 -m hpi gen-launcher-vl top
if test $? -ne 0; then exit 1; fi

python3 -m hpi -m my_tb gen-dpi
if test $? -ne 0; then exit 1; fi

CFLAGS="${CFLAGS} `python3-config --cflags`"
LDFLAGS="${LDFLAGS} `python3-config --ldflags`"

verilator --cc --exe top.sv launcher_vl.cpp pyhpi_dpi.c \
  -CFLAGS "${CFLAGS}" -LDFLAGS "${LDFLAGS}"
if test $? -ne 0; then exit 1; fi


#gcc ${CFLAGS} -c pyhpi_dpi.c
#if test $? -ne 0; then exit 1; fi

#g++ ${CFLAGS} -c launcher_vl.cpp
#if test $? -ne 0; then exit 1; fi

make -C obj_dir -f Vtop.mk
if test $? -ne 0; then exit 1; fi

./obj_dir/Vtop
if test $? -ne 0; then exit 1; fi

#g++ -o foo ./obj_dir/Vtop__ALL.a `python3-config --ldflags`
#if test $? -ne 0; then exit 1; fi

# Remove generated files
rm *.cpp *.c
rm -rf obj_dir __pycache__
