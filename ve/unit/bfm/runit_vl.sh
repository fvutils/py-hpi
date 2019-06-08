#!/bin/sh -x

# auto-set PYTHONPATH
cwd=`pwd`
export PYTHONPATH=$cwd/../../../src:$PYTHONPATH

python3 -m hpi gen-launcher-vl top -clk clk=1ns 
if test $? -ne 0; then exit 1; fi

python3 -m hpi gen-bfm-wrapper -m my_tb simple_bfm -type sv-dpi
if test $? -ne 0; then exit 1; fi

python3 -m hpi gen-dpi -m my_tb
if test $? -ne 0; then exit 1; fi

# Query required compilation/linker flags from Python
CFLAGS="${CFLAGS} `python3-config --cflags`"
LDFLAGS="${LDFLAGS} `python3-config --ldflags`"

verilator --cc --exe -Wno-fatal --trace \
	top.sv simple_bfm.sv \
	launcher_vl.cpp pyhpi_dpi.c \
	-CFLAGS "${CFLAGS}" -LDFLAGS "${LDFLAGS}"
if test $? -ne 0; then exit 1; fi

# Build the Verilator image
make -C obj_dir -f Vtop.mk
if test $? -ne 0; then exit 1; fi

# Run the simulation
./obj_dir/Vtop +hpi.load=my_tb +vl.timeout=1ms +vl.trace
if test $? -ne 0; then exit 1; fi

# Remove generated files
rm *.cpp *.c simple_bfm.sv
rm -rf obj_dir __pycache__
