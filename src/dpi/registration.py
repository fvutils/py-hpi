#****************************************************************************
#* registration.py
#*
#* Copyright 2019 Matthew Ballance
#*
#****************************************************************************

class tf:
    
    def __init__(self, is_f, is_imp, ret : str, sig : [str]):
        self.is_f   = is_f
        self.is_imp = is_imp
        self.ret    = self.parsetype(ret)
        self.sig    = []
        for s in sig:
            self.sig.append(self.parsetype(s))
        self.tf_name = None;
        
    def parsetype(self, t):
        if t == None:
            return "void"
        else:
            
            if t.startswith("byte"):
                print("int8_t")
                t = t[len("byte"):].strip()
            elif t.startswith("shortint"):
                print("int16_t")
                t = t[len("shortint"):].strip()
            elif t.startswith("int"):
                print("int32_t")
                t = t[len("int"):].strip()
            elif t.startswith("longint"):
                print("int64_t")
                t = t[len("longint"):].strip()
            elif t.startswith("string"):
                print("string")
                t = t[len("string"):].strip()
            else:
                print("Error:")
                
            if t.startswith("unsigned"):
                print("is unsigned")
                t = t[len("unsigned"):].strip()
        

# Map of <import_name> -> <tf closure>
tasks = {}

class import_task():
    
    def __init__(self, sig : [str]):
        print("import_task: ")
        self.m_tf = tf(False, True, None, sig)
        for p in sig:
            print("Parameter type: " + p)
            
    def __call__(self, func):
        print("call");
        self.m_tf.tf_name = func.__name__
        tasks[func.__name__] = self.m_tf
        return func

class export_task():
    
    # Save a handle to the annotated method that we can call
    def __init__(self, ret, sig : [str]):
        pass
    
    def __call__(self, func):
        return func

def import_function(ret,sig : [str]):
    # Should return a closure that will call the relevant DPI function
    pass

def export_function(ret,sig : [str]):
    # Save a handle to the annotated method that we can call
    pass
