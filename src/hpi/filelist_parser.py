'''
Created on Jun 2, 2019

@author: ballance
'''

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
        self.unget_c = -1
        
    
    def parse(self, ) -> [str]:
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
                
                parser = FilelistParser(basedir, filelist, self.processed_paths)
                
                sub_args = parser.parse()
                
                for arg in sub_args:
                    ret.append(arg)
            else:
                ret.append(self.expand(tok))
                
        return ret
    
    def readtok(self) -> str:
        ret = None
        
        while True:
            c = self.getch()
            
            if c == -1:
                break
            
            if c == '/':
                c2 = self.getch()
                
                if c2 == '*':
                    cc1 = -1
                    cc2 = -1
                    
                    while True:
                        c = self.getch()
                        
                        if c == -1:
                            break
                        
                        cc2 = cc1
                        cc1 = c
                        
                        if cc1 == '/' and cc2 == '*':
                            break
                    continue
                elif c2 == '/':
                    while True:
                        c = self.getch()
                    
                        if c == -1 or c == '\n':
                            self.ungetch(c)
                            break
                else:
                    self.ungetch(c)
            elif c.isspace():
                while True:
                    c = self.getch()
                    if c == -1 or c.isspace():
                        break

            if c == '"':
                last_c = -1
                ret.append(c)
                
                while True:
                    c = self.getch()
                    
                    if c == '"' and last_c == '\\':
                        ret[len(ret)-1] = c
                    else:
                        ret.append(c)
                        
                    if c == -1 or (c == '"' and last_c != '\\'):
                        break
            else:
                ret.append(c)
                while True:
                    c = self.getch()
                    if c == -1 or c.isspace():
                        self.ungetch(c)
                        break
                    else:
                        ret.append(c)
            
        return ret
    
    def expand(self, arg : str) -> str:
        pass
   
    def getch(self) -> str:
        ret = -1
        
        if self.unget_c != -1:
            ret = self.unget_c
            self.unget_c = -1
        else:
            ret = self.fp.read(1)

        return ret
    
    def ungetch(self, c):
        self.unget_c = c
   
    def expand(self, arg : str) -> str:
        ret = ""
        
        i=0
        while i < len(arg):
            if arg[i] == '$':
                if arg[i+1] = '{':
                    expect_closebrace = True
                    i += 2
                else:
                    expect_closebrace = False
                    
                j = i
                while j < len(arg):
                    c = arg[i]
            else:
                ret += arg[i]
                
            i += 1
        
        return ret
    