'''
Created on Jun 2, 2019

@author: ballance
'''

import os

class FilelistParser():
    
    def __init__(self, 
                 filelist : str, 
                 cwd : str, 
                 is_caps_f : bool, 
                 processed_paths : [str] = [],
                 parent=None):
        self.parent = parent;
        self.filelist = filelist
        self.cwd = cwd
        self.processed_paths = processed_paths
        self.fp = open(filelist, mode="rb")
        self.unget_c = ""
        
    
    def parse(self) -> [str]:
        ret = []
        
        if self.filelist in self.processed_paths:
            return ret
       
        self.processed_paths.append(self.filelist)
      
        while True:
            tok = self.readtok();
            if tok == None:
                break
            
            if tok == "-f" or tok == "-F":
                filelist = self.expand(self.readtok())
                basedir = self.cwd
                
                parser = FilelistParser(filelist, self.cwd, self.processed_paths)
                
                sub_args = parser.parse()
                
                for arg in sub_args:
                    ret.append(arg)
            else:
                ret.append(self.expand(tok))
                
        return ret
    
    def readtok(self) -> str:
        ret = ""

        while True:
            c = self.getch()
            
            if c == "":
                break
            
            if c == '/':
                c2 = self.getch()
                
                if c2 == '*':
                    cc1 = -1
                    cc2 = -1
                    
                    while True:
                        c = self.getch()
                        
                        if c == "":
                            break
                        
                        cc2 = cc1
                        cc1 = c
                        
                        if cc1 == '/' and cc2 == '*':
                            break
                    continue
                elif c2 == '/':
                    while True:
                        c = self.getch()
                    
                        if c == "" or c == '\n':
                            self.ungetch(c)
                            break
                else:
                    self.ungetch(c)
            elif c.isspace():
                while True:
                    c = self.getch()
                    if c == "" or not c.isspace():
                        break
                self.ungetch(c)
                continue
            else:
                # We have a non-WS character
                break

        if c == '"':
            last_c = -1
            ret += c
                
            while True:
                c = self.getch()
                    
                if c == '"' and last_c == '\\':
                    ret[len(ret)-1] = c
                else:
                    ret.append(c)
                       
                if c == "" or (c == '"' and last_c != '\\'):
                    break
        else:
            ret += c
            while True:
                c = self.getch()
                if c == "" or c.isspace():
                    self.ungetch(c)
                    break
                else:
                    ret += c

        if len(ret) > 0:
            return ret
        else:
            return None
    
    def getch(self) -> str:
        ret = ""
        
        if self.unget_c != "":
            ret = self.unget_c
            self.unget_c = ""
        else:
            b = self.fp.read(1)
            if len(b) > 0:
                ret = b.decode()
            else:
                ret = ""

        return ret
    
    def ungetch(self, c):
        self.unget_c = c
   
    def expand(self, arg : str) -> str:
        ret = ""
        
        i=0
        while i < len(arg):
            if arg[i] == '$':
                if arg[i+1] == '{':
                    expect_closebrace = True
                    i += 2
                else:
                    expect_closebrace = False
                    
                j = i
                while j < len(arg):
                    c = arg[j]
                    
                    if not c.isalpha() and not c.isnumeric() and (c != '_'):
                        break
                    j += 1
                    
                key = arg[i:j]
                
                if key in os.environ.keys():
                    val = os.environ[key]
                else:
                    val = ""
                    
                if expect_closebrace == False:
                    i=j-1
                else:
                    i=j
                    
                ret += val
            else:
                ret += arg[i]
                
            i += 1
        
        return ret
    