'''
Created on May 22, 2019

@author: ballance
'''
from hpi.rgy import entry_list

class plusarg:
    def __init__(self, p, v):
        print("p=" + p + " v=" + v)
        self.p = p;
        self.v = v;
        
prv_argv = []
prv_plusargs = []

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

def tb_main():
    global entry_list
    print("Hello from tb_main")
   
    # TODO: Select a default entry if one exists
    for e in entry_list.keys():
        print("Entry: " + e)

    entry_l = get_plusarg_vals("+hpi.entry")
    entry = None
    if entry_l == None:
        if len(entry_list.keys()) == 0:
            raise Exception("No +hpi.entry specified and no registered entries")
        elif len(entry_list.keys()) == 1:
            entry = entry_list[next(entry_list.keys())]
        else:
            raise Exception("No +hpi.entry specified and multiple registered entries")
    elif len(entry_l) == 1:
        e = entry_l[0]
        if e.find(".") != -1:
            e = e[e.find(".")+1:]
            
        if e in entry_list.keys():
            entry = entry_list[e]
        else:
            raise Exception("Specified entry \"" + e + "\" not in registered entries")
    else:
        raise Exception("Multiple +hpi.entry options specified")

    print("--> entry") 
    entry()
    print("<-- entry") 

def tb_init(argv):
    global prv_plusargs
    global prv_argv
    print("tb_init: " + str(argv))
    
    prv_argv = argv;
    
    for arg in argv:
        if arg.startswith("+"):
            if arg.find('=') != -1:
                prv_plusargs.append(plusarg(
                    arg[:arg.find('=')],
                    arg[arg.find('=')+1:]));
            else:
                prv_plusargs.append(plusarg(arg, ""))

    for p in prv_plusargs:                
        if p.p == "+hpi.load":
            print("Loading \"" + p.v + "\"")
            try:
                __import__(p.v)
            except:
                print("Error: loading " + p.v)
        elif p.p == "+hpi.entry":
            if p.v.find("."):
                # Load the module associated with the entry
                m = p.v[:p.v.find(".")]
                try:
                    __import__(m)
                except:
                    print("Error: loading " + m)
                

