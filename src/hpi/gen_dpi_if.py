#****************************************************************************
#* gen_dpi_if.py
#*
#* Code to generate the DPI wrapper interface
#****************************************************************************
'''
Created on May 19, 2019

@author: ballance
'''

import hpi
import argparse
import os
from hpi.rgy import bfm, tf_param
from hpi.rgy import tf_decl
from string import Template
from hpi.bfm_info import bfm_info

pyhpi_dpi_template = '''
/****************************************************************************
 * ${filename}
 *
 * Note: This file is generated. Do Not Edit
 *
 * Provides a DPI interface between SystemVerilog and Python. 
 * Generated using the command: ${command}
 ****************************************************************************/
#include <stdint.h>
#include "Python.h"
    
#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

${dpi_prototypes}

// Prototype for initialization function
int pyhpi_init(void);

// Initialization function for the launcher. Called before the first BFM
// is registered
int pyhpi_launcher_init(void);

static int pyhpi_register_bfm(const char *tname, const char *iname);

// DPI functions
void *svGetScope(void);
void svSetScope(void *);

#ifdef __cplusplus
}
#endif /* __cplusplus */

static void **prv_scope_list   = 0;
static int prv_scope_list_idx = 0;
static int prv_scope_list_len = 0;
static int prv_initialized = 0;

// TODO: need to import hpi module

// Import Task/Function implementations
${dpi_tf_impl}

// TODO: export-tf implementations

static PyObject *set_context(PyObject *self, PyObject *args) {
    int id;
    if (!PyArg_ParseTuple(args, "i", &id)) {
        return 0;
    }
    
    svSetScope(prv_scope_list[id]);
    
    return PyLong_FromLong(id);
}

// Python module initialization table
static PyMethodDef hpi_exp_methods[] = {
    {"set_context", &set_context, METH_VARARGS, ""},
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

static PyObject *PyInit_hpi_e(void) {
    return PyModule_Create(&hpi_e);
}

static int pyhpi_register_bfm(const char *tname, const char *iname) {
    PyObject *hpi, *reg_func;
    int ret = 0;
    
    if (!prv_initialized) {
        pyhpi_launcher_init();
        prv_initialized = 1;
    }
  
    if (prv_scope_list_idx >= prv_scope_list_len) {
        void *old = prv_scope_list;
        prv_scope_list = (void **)malloc(sizeof(void *)*prv_scope_list_len+64);
        if (old) {
            memcpy(prv_scope_list, old, sizeof(void *)*prv_scope_list_idx);
            free(old);
        }
    }
    prv_scope_list[prv_scope_list_idx] = svGetScope();
    ret = prv_scope_list_idx;
    prv_scope_list_idx++;

    // Call Python side to create and register the BFM instance
    if (!(hpi = PyImport_ImportModule("hpi"))) {
        fprintf(stdout, "Error: failed to import module 'hpi'\\n");
        return -1;
    }
    reg_func = PyObject_GetAttrString(hpi, "register_bfm");
    PyObject_CallFunctionObjArgs(reg_func, 
        PyUnicode_FromString(tname),
        PyUnicode_FromString(iname), 
        PyLong_FromLong(ret),
        0);
    
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

def gen_c_paramlist(params):
    ret = ""
    
    if len(params) == 0:
        ret += "void"
    else:                
        for p in params:
            ret += typemap[p.ptype]
            if p.ptype != 's':
                ret += " "
            ret += p.pname + ", "
            
        ret = ret[:len(ret)-2]
    return ret

def gen_c_ret_type(t):
    if t == None:
        ret = "void "
    else:
        ret = typemap[t]
        if t != 's':
            ret += " "
    return ret

def gen_dpi_prototype(tf : tf_decl):
    ret = gen_c_ret_type(tf.rtype)

    if tf.is_imp and tf.bfm != None:
        if len(tf.params) == 0:
            ret += tf.tf_name() + "(int id);\n"
        else:
            ret += tf.tf_name() + "(int id, " + gen_c_paramlist(tf.params) + ");\n"
    else:
        ret += tf.tf_name() + "(" + gen_c_paramlist(tf.params) + ");\n"
        
    return ret

def gen_register_bfm_prototype(bfm_name : str):
    return "int " + bfm_name + "_register(const char *iname);\n"

def gen_dpi_prototypes():
    ret = ""

    # First deal with global methods
    for tf in hpi.rgy.tf_global_list:
        ret += gen_dpi_prototype(tf)

    # Now, generate BFM-specific methods
    for bfm_name in hpi.rgy.bfm_type_map.keys():
        info = hpi.rgy.bfm_type_map[bfm_name]
        ret += gen_register_bfm_prototype(bfm_name)
        for tf in info.tf_list:
            ret += gen_dpi_prototype(tf)
        
    return ret

def gen_hpi_method_table_entry(tf : tf_decl):
    return "{\"" + tf.tf_name() + "\", &" + tf.tf_name() + "_py, METH_VARARGS, \"\"},\n"

def gen_hpi_method_table_entries():
    ret = ""
    
    for tf in hpi.rgy.tf_global_list:
        if tf.is_imp == False:
            ret += "    " + gen_hpi_method_table_entry(tf)

    # Now, generate BFM-specific methods
    for bfm_name in hpi.rgy.bfm_type_map.keys():
        print("bfm: " + bfm_name)
        info = hpi.rgy.bfm_type_map[bfm_name]
        for tf in info.tf_list:
            if tf.is_imp == False:
                ret += "    " + gen_hpi_method_table_entry(tf)

    return ret

def gen_py_paramlist(params):
    ret = ""
    for p in params:
        print("param: " + p.pname)
        if p.ptype == 's':
            ret += "PyUnicode_FromString(" + p.pname + "), "
        else:
            ret += "PyLong_FromLong(" + p.pname + "), "

    return ret
    
def gen_dpi_global_imp_tf_impl(tf : tf_decl):
    ret = gen_c_ret_type(tf.rtype)
    
    ret += tf.tf_name() + "(" + gen_c_paramlist(tf.params) + ") {\n"
    ret += "    PyObject *module, *call_ret, *f;\n"
    ret += "    module = PyImport_ImportModule(\"" + tf.module + "\");\n"
    ret += "    if (!module) {\n"
    ret += "        fprintf(stdout, \"Error: failed to import module " + tf.module + "\\n\");\n"
    ret += "        return 0;\n"
    ret += "    }\n"
    ret += "    f = PyObject_GetAttrString(module, \"" + tf.tf_name() + "\");\n";
    ret += "    if (!f) {\n"
    ret += "        fprintf(stdout, \"Error: failed to find function " + tf.tf_name() + "\\n\");\n"
    ret += "        return 0;\n"
    ret += "    }\n"
    ret += "    call_ret = PyObject_CallFunctionObjArgs(f, " + gen_py_paramlist(tf.params) + "0);\n"
    # TODO: detect a DPI exception and return '1'
    ret += "    Py_DECREF(f);\n"
    ret += "    Py_DECREF(module);\n"
   
    ret += "    return 0;\n"
    ret += "}\n"
    ret += "\n"
    
    return ret

def gen_dpi_global_exp_tf_impl(tf : tf_decl):
    return "// TODO: global export function for \"" + tf.tf_name() + "\"\n"

def gen_dpi_global_tf_impl(tf : tf_decl):
    if tf.is_imp:
        return gen_dpi_global_imp_tf_impl(tf)
    else:
        return gen_dpi_global_exp_tf_impl(tf)
    
def gen_dpi_bfm_imp_tf_impl(tf : tf_decl):
    ret = gen_c_ret_type(tf.rtype)
   
    if len(tf.params) != 0:
        ret += tf.tf_name() + "(int id, " + gen_c_paramlist(tf.params) + ") {\n"
    else:
        ret += tf.tf_name() + "(int id) {\n"
        
    ret += "    PyObject *hpi = PyImport_ImportModule(\"hpi\");\n";
    ret += "    PyObject *bfm_list = PyObject_GetAttrString(hpi, \"bfm_list\");\n"
    ret += "    PyObject *bfm = PyList_GetItem(bfm_list, id);\n"
    ret += "    PyObject *yield = PyObject_GetAttrString(hpi, \"int_thread_yield\");\n"
    ret += "    // TODO: pass arguments\n"
    ret += "    PyObject_CallMethodObjArgs(bfm, PyUnicode_FromString(\"" + tf.fname + "\"), ";
    ret += "0);\n"
    ret += "    PyObject_CallFunctionObjArgs(yield, 0);\n"
    ret += "    Py_DECREF(hpi);\n";
    ret += "    return 0;\n"
    
    # TODO: call Python side
    ret += "}\n"
    
    return ret

def gen_dpi_bfm_register_impl(bfm : bfm_info):
    ret = "int " + bfm.tname + "_register(const char *iname) {\n"
    ret += "    return pyhpi_register_bfm(\"" + bfm.tname + "\", iname);\n";
    ret += "}\n"
    return ret

def gen_dpi_declare_param_var(p : tf_param):
    if p.ptype == 's':
        return "char *" + p.pname + ";\n"
    else:
        return typemap[p.ptype] + " " + p.pname + ";\n"
    
def gen_py_argparse(params : [tf_param]):
    ret = "    if (!PyArg_ParseTuple(args, \"i"
    
    for p in params:
        ret += p.ptype[0]
        
    ret += "\", "

    ret += "&id, "    
    for p in params:
        ret += "&" + p.pname + ", "
   
    # Trim the last comma
    ret = ret[:len(ret)-2]
   
    ret += ")) {\n"
    ret += "        return 0;\n"
    ret += "    }\n" 
    return ret;

def gen_dpi_bfm_exp_tf_impl(tf : tf_decl):
    ret = "PyObject *" + tf.tf_name() + "_py(PyObject *self, PyObject *args) {\n"
    ret += "    unsigned int id;\n"
#    ret += "    fprintf(stdout, \"--> entry to " + tf.tf_name() + "\\n\");\n"
#    ret += "    fflush(stdout);\n"
    
    if len(tf.params) != 0:
        for p in tf.params:
            ret += "    " + gen_dpi_declare_param_var(p)

#        ret += "    fprintf(stdout, \"--> getting args to " + tf.tf_name() + "\\n\");\n";
#        ret += "    fflush(stdout);\n"
        ret += gen_py_argparse(tf.params)
#        ret += "    fprintf(stdout, \"--> getting args to " + tf.tf_name() + "\\n\");\n";
#        ret += "    fflush(stdout);\n"

    # Set the DPI context
    ret += "    svSetScope(prv_scope_list[id]);\n"
    # Finally, call the actual export
#    ret += "    fprintf(stdout, \"--> calling " + tf.tf_name() + "\\n\");\n";
#    ret += "    fflush(stdout);\n"
    if len(tf.params) == 0:
        ret += "    " + tf.tf_name() + "();\n"
    else:
        ret += "    " + tf.tf_name() + "("
        for p in tf.params:
            ret += p.pname + ", "
        ret = ret[:len(ret)-2]
        ret += ");\n"
     
#    ret += "    fprintf(stdout, \"<-- calling " + tf.tf_name() + "\\n\");\n";
#    ret += "    fflush(stdout);\n"
    ret += "    return PyLong_FromLong(0);\n"
    ret += "}\n"
    return ret
    
def gen_dpi_bfm_tf_impl(tf : tf_decl):
    if tf.is_imp:
        return gen_dpi_bfm_imp_tf_impl(tf)
    else:
        return gen_dpi_bfm_exp_tf_impl(tf)

def gen_dpi_tf_impl():
    ret = ""
    
    for tf in hpi.rgy.tf_global_list:
        if tf.is_imp == True:
            ret += gen_dpi_global_tf_impl(tf)

    # Now, generate BFM-specific methods
    for bfm_name in hpi.rgy.bfm_type_map.keys():
        info = hpi.rgy.bfm_type_map[bfm_name]
        ret += gen_dpi_bfm_register_impl(info)
        for tf in info.tf_list:
            ret += gen_dpi_bfm_tf_impl(tf)

    return ret
    
def gen_dpi(args):
    if args.o == None:
        args.o = "pyhpi_dpi.c"

    template_params = {}
    template_params['filename'] = os.path.basename(args.o)
    template_params['dpi_prototypes'] = gen_dpi_prototypes()
    template_params['hpi_method_table_entries'] = gen_hpi_method_table_entries()
    template_params['dpi_tf_impl'] = gen_dpi_tf_impl()
    template_params['command'] = "TODO"
    
    fh = open(args.o, "w")
    template = Template(pyhpi_dpi_template)
    fh.write(template.substitute(template_params))
    
    fh.close()
    