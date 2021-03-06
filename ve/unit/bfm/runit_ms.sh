#!/bin/sh -x

# TODO: auto-set PYTHONPATH (?)
cwd=`pwd`
export PYTHONPATH=$cwd/../../../src:$PYTHONPATH

ncpu=`cat /proc/cpuinfo | grep processor | wc -l`

python3 -m hpi gen-launcher-sv
if test $? -ne 0; then exit 1; fi

python3 -m hpi -m my_tb gen-dpi
if test $? -ne 0; then exit 1; fi


CFLAGS="`python3-config --cflags`"
#CFLAGS="-I/usr/include/python3.6m -I/usr/include/python3.6m"
LDFLAGS="${LDFLAGS} `python3-config --ldflags`"


vlib work
vlog -sv +define+HAVE_HDL_CLOCKGEN simple_bfm.sv top.sv pyhpi_sv.sv
if test $? -ne 0; then exit 1; fi
vlog -ccflags "${CFLAGS}" pyhpi_sv_dpi.c pyhpi_dpi.c
if test $? -ne 0; then exit 1; fi

time vsim -batch -do "vcd add -r /*; run 1ms; quit -f" top pyhpi_sv -ldflags "${LDFLAGS}" \
  +hpi.entry=my_tb.run_my_tb
exit 0

#gcc ${CFLAGS} -c pyhpi_dpi.c
#if test $? -ne 0; then exit 1; fi

#g++ ${CFLAGS} -c launcher_vl.cpp
#if test $? -ne 0; then exit 1; fi

make -j${ncpu} -C obj_dir -f Vtop.mk
if test $? -ne 0; then exit 1; fi

time ./obj_dir/Vtop +hpi.entry=my_tb.run_my_tb
if test $? -ne 0; then exit 1; fi

#g++ -o foo ./obj_dir/Vtop__ALL.a `python3-config --ldflags`
#if test $? -ne 0; then exit 1; fi

# Remove generated files
rm *.cpp *.c
rm -rf obj_dir __pycache__
