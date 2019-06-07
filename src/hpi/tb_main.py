'''
Created on May 22, 2019

@author: ballance
'''
import os
from hpi.rgy import entry_list
from hpi.scheduler import create_root_thread
from hpi.scheduler import thread_yield
from hpi.filelist_parser import FilelistParser

class plusarg:
    def __init__(self, p, v):
        self.p = p;
        self.v = v;
        
prv_argv = []
prv_plusargs = []
prv_objection_count = 0

def raise_objection():
    global prv_objection_count
    prv_objection_count += 1
    
def drop_objection():
    global prv_objection_count
    if prv_objection_count >= 1:
        prv_objection_count -= 1
        
    if prv_objection_count == 0:
        finish()

def finish():
        try:
            import hpi_l
            hpi_l.finish()
        except:
            print("Error: failed to call 'hpi_l.finish'")
            
def get_plusarg_vals(key):
    global prv_plusargs
    ret = []
    
    for p in prv_plusargs:
        if p.p == key:
            ret.append(p.v)

    if len(ret) == 0:
        return None
    else:
        return ret

def get_plusarg(key, dflt=None):
    ret = None
    
    for p in prv_plusargs:
        if p.p == key:
            if p.v == None:
                ret = dflt
            else:
                ret = p.v
            break

    return ret

def tb_main():
    global entry_list
   
    # TODO: Select a default entry if one exists
#    print("entry_list: size=" + str(len(entry_list.keys())))
#    for e in entry_list.keys():
#        print("Entry: " + e)

    entry_l = get_plusarg_vals("hpi.entry")
    entry = None
    if entry_l == None:
        if len(entry_list.keys()) == 0:
            raise Exception("No +hpi.entry specified and no registered entries")
        elif len(entry_list.keys()) == 1:
            entry = entry_list[list(entry_list.keys())[0]]
        else:
            raise Exception("No +hpi.entry specified and multiple registered entries")
    elif len(entry_l) == 1:
        e = entry_l[0]
        if e.rfind('.') != -1:
            e = e[e.rfind('.')+1:]
            
        if e in entry_list.keys():
            entry = entry_list[e]
        else:
            raise Exception("Specified entry \"" + e + "\" not in registered entries")
    else:
        raise Exception("Multiple +hpi.entry options specified")

    # TODO: should launch entry() in a new hpi thread
    create_root_thread(entry)
    
    # Now, wait until any launched threads are dormant
    for i in range(1000):
        if thread_yield() == False:
#            print("Stable: " + str(i))
            break

    if prv_objection_count == 0:
        print("Warning: no objections raised by initial threads")
        finish()
        
    # TODO: should check to ensure that the hpi thread suspends in a 
    # reasonable amount of time

def tb_init(argv):
    global prv_plusargs
    global prv_argv
    timeout = 1000000 # 1ms (in ns)
    print("tb_init: " + str(argv))
    
    # Expand out arguments
    i=0
    prv_argv = []
    cwd = os.getcwd()
    while i < len(argv):
        if argv[i] == '-f' or argv[i] == '-F':
            filelist = argv[i+1]
            print("filelist=\"" + filelist + "\"")
            parser = FilelistParser(filelist, cwd, 
                    (argv[i] == '-F'))
            fl_argv = parser.parse()
            
            for arg in fl_argv:
                prv_argv.append(arg)
                
            i+=1
        else:
            prv_argv.append(argv[i])
        i+=1
    
    i=0;
    while i < len(prv_argv):
        arg = prv_argv[i]
        if arg.startswith("+"):
            key = arg[1:]
            if key.find('=') != -1:
                prv_plusargs.append(plusarg(
                    key[:key.find('=')],
                    key[key.find('=')+1:]));
            else:
                prv_plusargs.append(plusarg(key, None))
        elif arg == "-f" or arg == "-F":
            filelist = prv_argv[i+1]
            print("TODO: handle filelist \"" + filelist + "\"")
            i += 1
        i += 1
            

    for p in prv_plusargs:                
        if p.p == "hpi.load":
            print("Loading \"" + p.v + "\"")
            try:
                __import__(p.v)
            except:
                print("Error: loading " + p.v)
        elif p.p == "hpi.entry":
            if p.v.find("."):
                # Load the module associated with the entry
                m = p.v[:p.v.find(".")]
                print("--> load module \"" + m + "\"")
                try:
                    __import__(m)
                except:
                    print("Error: loading " + m)
                    raise
                print("<-- load module \"" + m + "\"")

    try:
        import hpi_l
        hpi_l.set_timeout(timeout)
    except:
        print("Error: caught an execption")

