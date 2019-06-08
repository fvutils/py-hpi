'''
Created on May 18, 2019

@author: ballance
'''

from string import Template

launcher = '''
/****************************************************************************
 * Verilator pyHPI Launcher for top "${top}"
 ****************************************************************************/
#include <stdint.h>
#include <stdio.h>
#include "Python.h"
#include "V${top}.h"
#ifdef VM_TRACE
${trace_headers}
#endif
#include <map>
#include <vector>
#include <string>
extern "C" int pyhpi_init();
extern "C" void pyhpi_launcher_init();

static V${top}                       *prv_top = 0;
static bool                          prv_initialized = false;
static PyObject                      *prv_args;
static PyObject                      *prv_hpi;
static uint64_t                      prv_simtime = 0;
static uint64_t                      prv_timeout = 1000000000000/1000; // 1ms
static bool                          prv_keep_running = true;
#ifdef VM_TRACE
${trace_fields}
#endif

/********************************************************************
 * get_simtime()
 *
 * Returns the current simulation time to the Python side
 ********************************************************************/
static PyObject *get_simtime(PyObject *self, PyObject *args) {
  return PyFloat_FromDouble(prv_simtime);
}

/********************************************************************
 * finish()
 *
 * Called from the Python side to terminate the simuation
 ********************************************************************/
static PyObject *finish(PyObject *self, PyObject *args) {
  prv_keep_running = false;
  return PyLong_FromLong(0);
}

static PyMethodDef hpi_l_methods[] = {
    {"get_simtime", &get_simtime, METH_VARARGS, ""},
    {"finish", &finish, METH_VARARGS, ""},
    { 0, 0, 0, 0}
};

static PyModuleDef hpi_l = {
        PyModuleDef_HEAD_INIT,
        "hpi_l",
        "",
        -1,
        hpi_l_methods,
        0,
        0,
        0,
        0
};

static PyObject *PyInit_hpi_l(void) {
    return PyModule_Create(&hpi_l);
}

// Initialization function called before the first BFM registers
void pyhpi_launcher_init() {
    if (prv_initialized) {
        return;
    }
    
    // Register the HPI module with Python
    // TODO: support a callback to signal activity (?)
    pyhpi_init();
    
    PyImport_AppendInittab("hpi_l", PyInit_hpi_l);
    
    // TODO: register launcher namespace methods to use for
    // - getting simulation time
    // - yielding to the simulation
    
    Py_Initialize();
   
    // TODO: perform some sort of initialization to ensure
    // BFMS are registered before running the testbench
    prv_hpi = PyImport_ImportModule("hpi");
    if (!prv_hpi) {
        fprintf(stdout, "Error: failed to import 'hpi' package\\n");
        fflush(stdout);
        return;
    }

    // TODO: check return
    PyObject *ret;
    
    ret = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(prv_hpi, "tb_init"),
        prv_args, 0);
        
    if (!ret) {
        fprintf(stdout, "Error calling tb_init\\n");
        PyErr_Print();
    }

    
    prv_initialized = true;
}

// TODO: advance-time function

// TODO: command-line arguments function

// TODO: clocking scheme

/********************************************************************
 * str2time()
 *
 * Convert a time-specification string to time in nS
 ********************************************************************/
static double str2time(const char *ts) {
    double ret = 0.0;
    char *eptr;
    
    if ((ret = strtod(ts, &eptr)) != 0.0) {
      // Now, determine the units
      switch (tolower(*eptr)) {
          case 'p':
              ret /= 1000;
              break;
              
          case 'n':
              ret *= 1.0;
              break;
              
          case 'u':
              ret *= 1000;
              break;
              
          case 'm':
              ret *= 1000000;
              break;
              
          case 's':
              ret *= 1000000000;
              break;
              
          default:
              fprintf(stdout, "Error: unknown time-unit specifier \\"%s\\"\\n", eptr);
              ret = 0.0;
      }
    } else {
        fprintf(stdout, "Error: failed to parse timeout specification \\"%s\\"\\n", ts);
    }
    
    return ret;
}

static void dump() {
#ifdef VM_TRACE
    if (prv_trace_o) {
      prv_trace_o->dump(prv_simtime);
    }
#endif
}

int main(int argc, char **argv) {
    bool started_tb = false;
    const char *trace_file = 0;
    // 1ms=0.001 - 3
    // 1ns = 0.000000001 - 9
    // 1.0
    // 1,000,000.0
    fprintf(stdout, "Hello from launcher for Verilator ${top}\\n");
    
    
    // First, check to see if a usage message is in order
    for (int i=1; i<argc; i++) {
        if (!strcmp(argv[i], "-h") ||
            !strcmp(argv[i], "--h") ||
            !strcmp(argv[i], "-help") ||
            !strcmp(argv[i], "--help") ||
            !strcmp(argv[i], "--?")) {
            fprintf(stdout, "TODO: help\\n");
            exit(1);
        }
    }

    // Capture all arguments
    prv_args = PyList_New(0);
    for (int i=1; i<argc; i++) {
        PyList_Append(prv_args, PyUnicode_FromString(argv[i]));
    }
    
    pyhpi_launcher_init();

    // Create top-level module
    prv_top = new V${top}();

    fprintf(stdout, "--> get_plusarg\\n");
    fflush(stdout);
    PyObject *trace_plusarg = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(prv_hpi, "get_plusarg"),
        PyUnicode_FromString("vl.trace"), 
        PyUnicode_FromString("${default_trace_file}"), 0);

    fprintf(stdout, "trace_plusarg=%p\\n", trace_plusarg);
    fflush(stdout);
    if (trace_plusarg && trace_plusarg != Py_None) {
#ifdef VM_TRACE
        trace_file = PyUnicode_AsUTF8(trace_plusarg);
#else
        fprintf(stdout, "Warning: +vl.trace specified, but --trace not specified during compilation\\n");
#endif
        fprintf(stdout, "trace_file=%s\\n", trace_file);
    }
    
#ifdef VM_TRACE
${trace_init}
#endif

${clocking_init}    
    
    // Determine whether the user has specified a timeout
    PyObject *timeout_plusarg = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(prv_hpi, "get_plusarg"),
        PyUnicode_FromString("vl.timeout"), 0);
          
    if (timeout_plusarg != Py_None) {
        fprintf(stdout, "Note: parse timeout specification\\n");
        prv_timeout = str2time(
                PyBytes_AsString(PyUnicode_AsUTF8String(timeout_plusarg)));
    } else {
        fprintf(stdout, "Note: no timeout specified\\n");
    }
    
    // Launch the testbench main code
    PyObject *ret = PyObject_CallFunctionObjArgs(
        PyObject_GetAttrString(prv_hpi, "tb_main"), 0);
    if (!ret) {
        fprintf(stdout, "Error calling tb_main\\n");
        PyErr_Print();
    }

    fprintf(stdout, "--> eval timeout=%lld\\n", prv_timeout);
    fflush(stdout);   
    while (prv_keep_running && prv_simtime < prv_timeout) {
${clocking_block}
    }
    fprintf(stdout, "<-- eval\\n");
    fflush(stdout);   
    
    prv_top->final();

    // TODO: check for trace enable (support VCD and FST?)
    
    // TODO: run python entry-point
//#ifdef VM_COVERAGE
//    VerilatedCov::write("sim.cdb");
//#endif
    
    // Done...
    Py_Finalize();
    
#ifdef VM_TRACE
${trace_fini}
#endif
    
    return 0;
}
'''

def gen_clocking_init(args):
    ret = ""

    for c in args.clk:
        clock_name = c[:c.find('=')]
        ret += "    prv_top->" + clock_name + " = 0;\n"
       
    ret += "    prv_top->eval();\n"
    
    return ret

def period_ps(period):
    unit = 0
    while unit < len(period) and ((period[unit] >= '0' and period[unit] <= '9') or period[unit] == '.'):
        unit += 1

    if unit == len(period):
        raise Exception("clock period \"" + period + "\" has no units")
    else:
        base = period[:unit]
        unit = period[unit:].lower()

    ret = int(base)
   
    if unit == "ps": 
        ret *= 1
    elif unit == "ns":
        ret *= 1000
    elif unit == "us":
        ret *= 1000000
    elif unit == "ms":
        ret *= 1000000000
    elif unit == "s":
        ret *= 1000000000000
    else:
        raise Exception("Unknown unit \"" + unit + "\" for clock period \"" + period + "\"")
   
    return ret;

def gen_clocking_block(args):
    ret = ""
    
#        prv_top->clk = 0;
#        prv_top->eval();
#        dump();
#        prv_simtime += 5; // 
#        prv_top->clk = 1;
#        prv_top->eval();
#        dump();
#        prv_simtime += 5; // 

    # TODO: simple way out for now
    for c in args.clk:
        clock_name = c[:c.find('=')]
        clock_period = c[c.find('=')+1:]
        
        p_ps = period_ps(clock_period) / 2
        
        ret += "        prv_top->" + clock_name + " = 0;\n"
        ret += "        prv_top->eval();\n"
        ret += "        dump();\n"
        ret += "        prv_simtime += " + str(p_ps) + "; // ps\n"
        ret += "        prv_top->" + clock_name + " = 1;\n"
        ret += "        prv_top->eval();\n"
        ret += "        dump();\n"
        ret += "        prv_simtime += " + str(p_ps) + "; // ps\n"
        
    return ret

def gen_launcher_vl(args):
    template = Template(launcher)
    
    # Load up modules that contain DPI tasks
    if args.m != None:
        print("loading modules")
        for m in args.m:
            print("loading " + str(m))
            __import__(m)    
    
    if args.clk == None or len(args.clk) == 0:
        raise Exception("No -clk specified")
    elif len(args.clk) > 1:
        raise Exception("Only one clock statement supported")

    for c in args.clk:
        if c.find('=') == -1:
            raise Exception("Clock specification \"" + c + "\" doesn't contain '='")
        
    # Need to 
    
    template_params = {}
    template_params['top'] = args.top
    template_params['clocking_init'] = gen_clocking_init(args)
    template_params['clocking_block'] = gen_clocking_block(args)
    if args.trace_fst == True:
        template_params['trace_headers'] = "#include \"verilated_fst_c.h\""
        template_params['trace_fields'] = "static VerilatedFstC                 *prv_trace_o = 0;"
        template_params['trace_init'] = '''
    if (trace_file) {
        Verilated::traceEverOn(true);  // Verilator must compute traced signals
        prv_trace_o = new VerilatedFstC();
        prv_top->trace(prv_trace_o, 99);  // Trace 99 levels of hierarchy
        prv_trace_o->open(trace_file);  // Open the dump file
    }
        '''
        template_params['default_trace_file'] = "sim.fst"
        template_params['trace_fini'] = '''
    if (prv_trace_o) {
        prv_trace_o->close();
    }
        '''
    else:
        template_params['trace_headers'] = "#include \"verilated_vcd_c.h\""
        template_params['trace_fields'] = "static VerilatedVcdC                 *prv_trace_o = 0;"
        template_params['trace_init'] = '''
    if (trace_file) {
        Verilated::traceEverOn(true);  // Verilator must compute traced signals
        prv_trace_o = new VerilatedVcdC();
        prv_top->trace(prv_trace_o, 99);  // Trace 99 levels of hierarchy
        prv_trace_o->open(trace_file);  // Open the dump file
    }
        '''
        template_params['default_trace_file'] = "sim.vcd"
        template_params['trace_fini'] = '''
    if (prv_trace_o) {
        prv_trace_o->close();
    }
        '''
    
    fh = open(args.o, "w")
    fh.write(template.substitute(template_params))
    fh.close()

