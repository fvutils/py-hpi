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

static std::vector<std::string>        prv_args;
static V${top}                        *prv_top = 0;

// TODO: advance-time function

// TODO: command-line arguments function

// TODO: clocking scheme

int main(int argc, char **argv) {
    fprintf(stdout, "Hello from launcher for Verilator ${top}\\n");

    // Capture all arguments
    for (int i=1; i<argc; i++) {
        prv_args.push_back(argv[i]);
    }

    // Register the HPI module with Python
    // TODO: support a callback to signal activity (?)
    pyhpi_init();
    
    // TODO: provide a way for the Python bench to advance simulation
    
    Py_Initialize();
   
    // TODO: determine modules to load

    // TODO: determine entry point to run
    
    // Create top-level module
    prv_top = new V${top}();

    fprintf(stdout, "--> eval\\n");
    fflush(stdout);   
    for (int i=0; i<10; i++) { 
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
