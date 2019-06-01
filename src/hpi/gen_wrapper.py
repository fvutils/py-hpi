'''
Created on May 31, 2019

@author: ballance
'''

from hpi.rgy import bfm_type_map, bfm_wrapper_type

def gen_bfm_wrapper(args):
    
    if args.bfm not in bfm_type_map.keys():
        raise Exception("BFM \"" + args.bfm + "\" is not registered")

    bfm = bfm_type_map[args.bfm]
    
    if hasattr(bfm.cls, "bfm_wrappers") == False:
        raise Exception("BFM \"" + args.bfm + "\" doesn't contain a 'bfm_wrappers' map")
    
    bfm_wrappers = getattr(bfm.cls, "bfm_wrappers")

    if args.type == 'sv-dpi':
        bfm_type = bfm_wrapper_type.SV_DPI
        if args.o == None:
            args.o = args.bfm + ".sv"
    elif args.type == 'vl-vpi':
        bfm_type = bfm_wrapper_type.VL_VPI
        if args.o == None:
            args.o = args.bfm + ".v"

    if bfm_type not in bfm_wrappers.keys():
        raise Exception("BFM \"" + args.bfm + "\" does not support wrapper \"" + args.type + "\"")

    wrapper_t = bfm_wrappers[bfm_type]
    
    if callable(wrapper_t):
        print("Calling wrapper")
        wrapper_t = wrapper_t()

    with open(args.o, "w") as f:
        f.write(wrapper_t)
