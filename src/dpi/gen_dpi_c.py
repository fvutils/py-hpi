'''
Created on May 7, 2019

@author: ballance
'''

import argparse
from dpi import registration


def gen_dpi_c_main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-m", action="append", help="Specifies a module to load")
    parser.add_argument("-o", help="Specifies output file")
    
    args = parser.parse_args()
   
    # Load up modules that contain DPI tasks
    for m in args.m:
        __import__(m)

    outfile = "pydpi_gasket.c"
    if args.o != None:
        outfile = args.o
   
    fh = open(outfile, "w")
    
    print("gen_dpi_c_main")
    
    for t in registration.tasks:
        print("t: " + str(t))

    fh.close()

if __name__ == "__main__":
    gen_dpi_c_main()