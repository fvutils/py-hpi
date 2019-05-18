'''
Created on May 15, 2019

@author: ballance
'''

try:
    # Bring in generated module that provides export-task wrappers
    # Ignore if we're running in wrapper-gen mode
    import hpi_e
except:
    pass

class bfm_info(object):
    
    def __init__(self, tname : str):
        self.tname = tname
        self.cls = None
        self.tf_list = []

    