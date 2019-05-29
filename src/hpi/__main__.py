#****************************************************************************
#* __main__.py
#*
#*
#****************************************************************************
import hpi
import argparse
import os
from hpi.rgy import bfm
from hpi.rgy import tf_decl
from string import Template
from hpi import launcher_vl
from hpi import launcher_sv
from hpi import gen_dpi_if

def gen_dpi_export_methods():
    pass

def list_bfms(args):
    print("list-bfms");
    
    for bfm in hpi.rgy.bfm_type_map.keys():
        print("bfm_name: " + str(bfm))

    
def gen_launcher_sv(args):
    fh = open(os.path.join(args.outdir, "pyhpi_sv_dpi.c"), "w")
    fh.write(launcher_sv.dpi_c)
    fh.close()
    
    fh = open(os.path.join(args.outdir, "pyhpi_sv.sv"), "w")
    fh.write(launcher_sv.dpi_sv)
    fh.close()
    
    
def main():
#    print("main " + str(len(hpi.bfm_list)))
#    hpi.bfm_list.append(None)
#    print("main " + str(len(hpi.bfm_list)))
    
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(title='subcommands')
    gen_dpi_cmd = subparsers.add_parser("gen-dpi")
    gen_dpi_cmd.add_argument("-verilator", action="store_true", help="Enables Verilator specifics")
    gen_dpi_cmd.add_argument("-o", help="Specifies output file")
    gen_dpi_cmd.set_defaults(func=gen_dpi_if.gen_dpi)
    
    list_bfms_cmd = subparsers.add_parser("list-bfms")
    list_bfms_cmd.set_defaults(func=list_bfms)
    
    gen_launcher_vl_cmd = subparsers.add_parser("gen-launcher-vl",
            help="Generate a launcher for Verilator")
    gen_launcher_vl_cmd.add_argument("-o", 
            default="launcher_vl.cpp",
            help="Specifies output file")
    gen_launcher_vl_cmd.add_argument("--trace",
            action="store_true",
            help="Enable VCD tracing from the launcher")
    gen_launcher_vl_cmd.add_argument("--trace-fst",
            action="store_true",
            help="Enable FST tracing from the launcher")
    gen_launcher_vl_cmd.add_argument("-clk", 
            action="append",
            help="Specifies clock to drive")
    gen_launcher_vl_cmd.add_argument("top",
            help="Specify the top-level module to run")
    gen_launcher_vl_cmd.set_defaults(func=launcher_vl.gen_launcher_vl)
    
    gen_launcher_sv_cmd = subparsers.add_parser("gen-launcher-sv",
            help="Generate a launcher for standard SV/DPI simulators")
    gen_launcher_sv_cmd.add_argument("-outdir", 
            default=".",
            help="Specifies the output directory")
    gen_launcher_sv_cmd.set_defaults(func=gen_launcher_sv)
    
    parser.add_argument("-m", action="append", help="Specifies a module to load")
    
    args = parser.parse_args()
   
    if hasattr(args, "func") == False:
        print("missing command")
        
    # Load up modules that contain DPI tasks
    if args.m != None:
        print("loading modules")
        for m in args.m:
            print("loading " + str(m))
            __import__(m)
            
    args.func(args)
   
if __name__ == "__main__":
    main()
    
