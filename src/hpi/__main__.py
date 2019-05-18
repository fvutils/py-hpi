#****************************************************************************
#* __main__.py
#*
#*
#****************************************************************************
import hpi
import argparse
import os
from hpi.rgy import bfm
from string import Template
from dpi.tf_decl import tf_decl

def gen_dpi_export_methods():
    pass

pyhpi_dpi_template = '''
/****************************************************************************
 * ${filename}.c
 *
 * Note: This file is generated. Do Not Edit
 *
 * Provides a DPI interface between SystemVerilog and Python
 ****************************************************************************/
#include <stdint.h>
#include "Python.h"
    
#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

${dpi_prototypes}

// Prototype for initialization function
int pyhpi_init(void);
int pyhpi_register_bfm(const char *tname, const char *iname);

// DPI functions
void *svGetScope(void);
void svSetScope(void *);

#ifdef __cplusplus
}
#endif /* __cplusplus */

static void *prv_scope_list   = 0;
static int prv_scope_list_idx = 0;
static int prv_scope_list_len = 0;

// TODO: need to import hpi module

// TODO: import-tf implementations

// TODO: export-tf implementations

static PyObject *set_context(PyObject *self, PyObject *args) {
    int id;
    if (!PyArg_ParseTuple(args, "i", &id)) {
        return 0;
    }
    
    svSetScope(prv_scope_list[id])
    
    return PyLong_FromLong(id)
}

// Python module initialization table
static PyMethodDef hpi_exp_methods[] = {
    {"set_context", &get_context, METH_VARARGS, ""},
${hpi_method_table_entries}
    { 0, 0, 0, 0}
};

static PyModuleDef hpi_e = {
        PyModuleDef_HEAD_INIT,
        "hpi_e",
        "",
        -1,
        hpi_exp_methods,
        0,
        0,
        0,
        0
};

static PyMODINIT_FUNC PyInit_hpi_e(void) {
    return PyModule_Create(&hpi_e);
}

int pyhpi_register_bfm(const char *tname, const char *iname) {
    int ret = 0;
  
    if (prv_scope_list_idx >= prv_scope_list_len) {
        void *old = prv_scope_list;
        prv_scope_list = (void *)malloc(sizeof(void *)*prv_scope_list_len+64);
        if (old) {
            memcpy(prv_scope_list, old, sizeof(void *)*prv_scope_list_idx);
            free(old);
        }
    }
    prv_scope_list[prv_scope_list_idx] = svGetScope();
    prv_scope_list_idx++;

    // TODO: call Python side
    
    return ret;
}

// initialization code implementations
int pyhpi_init(void) {
  // Add the exports module to the initialization table
  PyImport_AppendInittab("hpi_e", PyInit_hpi_e);
  return 1;
}

'''

typemap = {
    "i": "int",
    "iu": "unsigned int",
    "h": "short",
    "hu": "unsigned short",
    "b": "char",
    "bu": "unsigned char",
    "l": "long long",
    "lu": "unsigned long long",
    "s": "const char *"
    }

def gen_dpi_prototype(tf : tf_decl):
    ret = ""

    if tf.rtype == None:
        ret += "  void"
    else:
        ret += "  " + typemap[tf.rtype]
        if tf.rtype != 's':
            ret += " "

    ret += tf.fname + "("

    if len(tf.params) == 0:
        ret += "void"
    else:                
        for p in tf.params:
            ret += typemap[p.ptype]
            if p.ptype != 's':
                ret += " "
            ret += p.pname
       
    ret += ");\n"
        
    return ret

def gen_dpi_prototypes():
    ret = ""

    print("gen_dpi_prototypes")
    # First deal with global methods
    for tf in hpi.rgy.tf_global_list:
        ret += gen_dpi_prototype(tf)

    # Now, generate BFM-specific methods
    for bfm_name in hpi.rgy.bfm_type_map.keys():
        info = hpi.rgy.bfm_type_map[bfm_name]
        for tf in info.tf_list:
            print("tf: " + tf.fname)
            ret += gen_dpi_prototype(tf)
        
    return ret

def gen_hpi_method_table_entry(tf : tf_decl):
    return "{\"" + tf.fname + "\", &" + tf.fname + ", METH_VARARGS, \"\"},\n"

def gen_hpi_method_table_entries():
    ret = ""
    
    for tf in hpi.rgy.tf_global_list:
        if tf.is_imp == False:
            ret += "    " + gen_hpi_method_table_entry(tf)

    # Now, generate BFM-specific methods
    for bfm_name in hpi.rgy.bfm_type_map.keys():
        info = hpi.rgy.bfm_type_map[bfm_name]
        for tf in info.tf_list:
            if tf.is_imp == False:
                ret += "    " + gen_hpi_method_table_entry(tf)

    return ret

def gen_dpi(args):
    if args.o == None:
        args.o = "pyhpi_dpi.c"

    template_params = {}
    template_params['filename'] = os.path.basename(args.o)
    template_params['dpi_prototypes'] = gen_dpi_prototypes()
    template_params['hpi_method_table_entries'] = gen_hpi_method_table_entries()
    
    fh = open(args.o, "w")
    template = Template(pyhpi_dpi_template)
    fh.write(template.substitute(template_params))
    
    fh.close()

def list_bfms(args):
    print("list-bfms");
    
    for bfm in hpi.rgy.bfm_type_map.keys():
        print("bfm_name: " + str(bfm))
        
def main():
#    print("main " + str(len(hpi.bfm_list)))
#    hpi.bfm_list.append(None)
#    print("main " + str(len(hpi.bfm_list)))
    
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(title='subcommands')
    gen_dpi_cmd = subparsers.add_parser("gen-dpi")
    gen_dpi_cmd.add_argument("-verilator", action="store_true", help="Enables Verilator specifics")
    gen_dpi_cmd.set_defaults(func=gen_dpi)
    
    list_bfms_cmd = subparsers.add_parser("list-bfms")
    list_bfms_cmd.set_defaults(func=list_bfms)
    
    parser.add_argument("-load-module", action="append", help="Specifies a module to load")
    parser.add_argument("-o", help="Specifies output file")
    
    args = parser.parse_args()
   
    if hasattr(args, "func") == False:
        print("missing command")
        
    # Load up modules that contain DPI tasks
    if args.load_module != None:
        print("loading modules")
        for m in args.load_module:
            print("loading " + str(m))
            __import__(m)
            
    args.func(args)
   
if __name__ == "__main__":
    main()
    
