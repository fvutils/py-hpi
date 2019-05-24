'''
Created on May 18, 2019

@author: ballance
'''

launcher = '''
/****************************************************************************
 * Verilator pyHPI Launcher for top "${top}"
 ****************************************************************************/
#include <stdint.h>
#include <stdio.h>
#include "Python.h"
#include "V${top}.h"
#include "verilated_vcd_c.h"
#include "verilated_fst_c.h"
#include <map>
#include <vector>
#include <string>
extern "C" int pyhpi_init();
extern "C" void pyhpi_launcher_init();

static V${top}                        *prv_top = 0;
static bool                            prv_initialized = false;
static PyObject                        *prv_args;

// Initialization function called before the first BFM registers
void pyhpi_launcher_init() {
    if (prv_initialized) {
        return;
    }
    
    fprintf(stdout, "TODO: pyhpi_launcher_init()\\n");
    
    // Register the HPI module with Python
    // TODO: support a callback to signal activity (?)
    pyhpi_init();
    
    // TODO: register launcher namespace methods to use for
    // - getting simulation time
    // - yielding to the simulation
    
    Py_Initialize();
   
    // TODO: determine modules to load
    PyObject *my_tb = PyImport_ImportModule("my_tb");
    
    // TODO: perform some sort of initialization to ensure
    // BFMS are registered before running the testbench
    PyObject *hpi = PyImport_ImportModule("hpi");
    if (!hpi) {
        fprintf(stdout, "Error: failed to import 'hpi' package\\n");
        return;
    }

    // TODO: check return
    PyObject *ret;
    
    ret = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(hpi, "tb_init"),
        prv_args, 0);
        
    if (!ret) {
        fprintf(stdout, "Error calling tb_init\\n");
    }

    // TOOD: set a delta-delay callback from which to kick off
    // the testbench
    ret = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(hpi, "tb_main"), 0);
    if (!ret) {
        fprintf(stdout, "Error calling tb_main\\n");
        PyErr_Print();
    }
    
    prv_initialized = true;
}

// TODO: advance-time function

// TODO: command-line arguments function

// TODO: clocking scheme

int main(int argc, char **argv) {
    fprintf(stdout, "Hello from launcher for Verilator ${top}\\n");

    // Capture all arguments
    prv_args = PyList_New(0);
    for (int i=1; i<argc; i++) {
        PyList_Append(prv_args, PyUnicode_FromString(argv[i]));
    }

    // Create top-level module
    prv_top = new V${top}();

    fprintf(stdout, "--> eval\\n");
    fflush(stdout);   
    for (int i=0; i<10000000; i++) { 
        prv_top->clk = 0;
        prv_top->eval();
        prv_top->clk = 1;
        prv_top->eval();
    }
    fprintf(stdout, "<-- eval\\n");
    fflush(stdout);   

    // TODO: check for trace enable (support VCD and FST?)
    
    // TODO: run python entry-point
    
    // Done...
    Py_Finalize();
    
    return 0;
}
'''
