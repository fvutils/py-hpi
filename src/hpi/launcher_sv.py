'''
Created on May 26, 2019

@author: ballance
'''

dpi_c = '''
/****************************************************************************
 * SystemVerilog DPI Launcher
 ****************************************************************************/
#include <stdint.h>
#include <stdio.h>
#include "Python.h"

#ifdef __cplusplus
extern "C" {
#endif

int pyhpi_init();
void pyhpi_launcher_init();
void *svGetScope(void);
void svSetScope(void *);
int acc_fetch_argc(void);
char **acc_fetch_argv(void);

static unsigned int                    prv_initialized = 0;
static void                            *prv_pkg_scope = 0;
static PyObject                        *prv_args;
static PyObject                        *prv_hpi;

// Initialization function called before the first BFM registers
void pyhpi_launcher_init() {
    PyObject *ret;
    if (prv_initialized) {
        return;
    }
    
    fprintf(stdout, "TODO: pyhpi_launcher_init()\\n");
    // Capture all arguments
    prv_args = PyList_New(0);
    {
      int argc = acc_fetch_argc();
      char **argv = acc_fetch_argv();
      int i;
      for (i=0; i<argc; i++) {
          PyList_Append(prv_args, PyUnicode_FromString(argv[i]));
      }
    }
    
    // Register the HPI module with Python
    // TODO: support a callback to signal activity (?)
    pyhpi_init();
    
    // TODO: register launcher namespace methods to use for
    // - getting simulation time
    // - yielding to the simulation
    
    Py_Initialize();
   
    // TODO: perform some sort of initialization to ensure
    // BFMS are registered before running the testbench
    prv_hpi = PyImport_ImportModule("hpi");
    if (!prv_hpi) {
        fprintf(stdout, "Error: failed to import 'hpi' package\\n");
        return;
    }

    ret = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(prv_hpi, "tb_init"),
        prv_args, 0);
        
    if (!ret) {
        fprintf(stdout, "Error calling tb_init\\n");
    }
    
    prv_initialized = 1;
}

int pyhpi_sv_launcher_init(void) {
    fprintf(stdout, "--> pyhpi_sv_launcher_init()\\n");
    prv_pkg_scope = svGetScope();
    pyhpi_launcher_init();
    fprintf(stdout, "<-- pyhpi_sv_launcher_init()\\n");
  return 1;
}

'''

dpi_sv = '''
package pyhpi_sv_pkg;
   
    task pyhpi_sv_tb_init();
        $display("--> tb_init");
        repeat (100) begin
            #0;
        end
        $display("<-- tb_init");
    endtask
    export "DPI-C" task pyhpi_sv_tb_init;

    import "DPI-C" context function int pyhpi_sv_launcher_init();
    int init = pyhpi_sv_launcher_init();
    
endpackage
'''
