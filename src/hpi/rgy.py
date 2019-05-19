#****************************************************************************
#* rgy.py
#*
#* BFM registration decorators and methods
#****************************************************************************
from hpi.bfm_info import bfm_info
from lib2to3.fixer_util import is_import

try:
    import hpi_e
except:
    pass

bfm_list = []
bfm_type_map = {}
bfm_inst_map = {}
tf_global_list = []

def get_bfm_info(tname : str) -> bfm_info:
    if tname in bfm_type_map.keys():
        return bfm_type_map[tname]
    else:
        print("Adding BFM \"" + tname + "\" to bfm_type_map")
        info = bfm_info(tname)
        bfm_type_map[tname] = info
        return info

def bfm(cls):
    # Register the BFM type
    print("Register bfm \"" + cls.__name__ + "\"")
    info = get_bfm_info(cls.__name__)
    info.cls = cls
    return cls

class tf_param():
    
    def __init__(self, pname : str, ptype : str):
        self.pname = pname
        self.ptype = ptype

class tf_decl():
    
    def __init__(self, 
                 is_imp : bool,
                 is_task : bool,
                 fname : str, 
                 rtype : str,
                 param_names : [str], 
                 param_types : str):
        self.is_imp = is_imp
        self.is_task = is_task
        self.fname = fname
        self.rtype = rtype
        self.bfm = None
        self.module = None
        self.params = []

        si = 0        
        for i in range(len(param_names)):
            param_name = param_names[i]
            if si < len(param_types):
                base_type = param_types[si]
                si += 1
                unsigned = False
                if base_type in ('b', 'h', 'i', 'l'):
                    if si < len(param_types) and param_types[si] == 'u':
                        base_type += 'u'
                        si += 1
                elif base_type in ('s'):
                    pass
                else:
                    raise Exception("Unknown type specifier for parameter \"" + param_name + 
                                    "\" in function \"" + fname + "\"")
                    
                param_type = param_types[i]
            else:
                param_type = "<unknown>"
            self.params.append(tf_param(param_name, base_type))

    def tf_name(self):
        if self.bfm == None:
            return self.fname
        else:
            return self.bfm.tname + "_" + self.fname
        
# An import task decorator is specified on a method that will
# be called by the HDL environment
class import_task(tf_decl):
    
    def __init__(self, tinfo : str = ""):
        self.tinfo = tinfo
    
    def __call__(self, func):
        fullname = func.__qualname__
        
        
        fi = func.__code__
        
        locals_idx = fullname.find("<locals>")
        if locals_idx != -1:
            fullname = fullname[locals_idx+len("<locals>."):]
            
        dot_idx = fullname.find(".")
        
        if dot_idx != -1:
            bfm_name = fullname[:dot_idx]
            info = get_bfm_info(bfm_name)
            tf = tf_decl(
                True,
                True,
                func.__name__,
                'i',
                fi.co_varnames[1:fi.co_argcount],
                self.tinfo)
            info.tf_list.append(tf)
            tf.bfm = info
        else:
            tf = tf_decl(
                True,
                False,
                func.__name__,
                'i',
                fi.co_varnames[0:fi.co_argcount],
                self.tinfo)
            tf.module = func.__module__
            tf_global_list.append(tf)

        print("func=" + str(func))            
        return func

# An export_task decorator is specified on a task that will
# forward to a task implemented by the HDL environment. No
# statements in the Python method's implementation will be
# executed.
#
# A class method shall be declared with self as the first
# parameter, just as with 
class export_task(tf_decl):
    
    def __init__(self, tinfo : str = ""):
        self.tinfo = tinfo
        
    def __call__(self, func):
        fullname = func.__qualname__

        fi = func.__code__
        
        locals_idx = fullname.find("<locals>")
        if locals_idx != -1:
            fullname = fullname[locals_idx+len("<locals>."):]
            
        dot_idx = fullname.find(".")
        
        if dot_idx != -1:
            bfm_name = fullname[:dot_idx];
            info = get_bfm_info(bfm_name)
            tf = tf_decl(
                False,
                True,
                bfm_name + "_" + func.__name__,
                'i',
                fi.co_varnames[1:fi.co_argcount],
                self.tinfo)
            info.tf_list.append(tf)
            
            def export_task_w(self,*args):
                # TODO: set appropriate context
                eval("hpi_e." + api_name + "(*args)")
            return export_task_w
        else:
            raise Exception("Cannot declare global method an export task")

class import_func(tf_decl):
    
    def __init__(self, rtype : str, tinfo : str):
        self.tinfo = tinfo
        self.rtype = rtype
        
    def __call__(self, func):
        fullname = func.__qualname__

        fi = func.__code__
        
        locals_idx = fullname.find("<locals>")
        if locals_idx != -1:
            fullname = fullname[locals_idx+len("<locals>."):]
            
        dot_idx = fullname.find(".")
        
        if dot_idx != -1:
            api_name = fullname[:dot_idx] + "_" + func.__name__
            info = get_bfm_info(api_name)
            tf = tf_decl(
                True,
                False,
                api_name + "_" + func.__name__,
                'i',
                fi.co_varnames[1:fi.co_argcount],
                self.tinfo)
            info.tf_list.append(tf)
        else:
            tf = tf_decl(
                True,
                False,
                func.__name__,
                self.rtype,
                fi.co_varnames[1:fi.co_argcount],
                self.tinfo)
            tf_global_list.append(tf)

        return func
    
def register_bfm(tname : str, iname : str):
    if tname not in bfm_type_map.keys():
        print("Error: BFM type \"" + tname + "\" is not registered")
        return -1
    
    ret : int = len(bfm_list)
    info = bfm_type_map[tname]
    inst = info.cls()
    
    inst.iname = iname
    inst.ctxt = 0; # TODO: 
    
    bfm_inst_map[iname] = inst
    bfm_list.append(inst)
    
    return ret

