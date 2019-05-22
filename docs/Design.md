
- Static global registration function that is called by all BFMs
  - Specifies type name of BFM and instance being registered

- BFM type is created for each registered type

# 

# Wrapper (better name?)
The wrapper provides the interface between the environment and python and between
python and the environment at runtime. 


# Launcher
The launcher provides the mechanism for starting and running the Python environment.
Launchers are environment-specific, though one launcher may be shared by multiple
similar environments. For example, a launcher for standard SystemVerilog simulators
can be shared by all simulators that provide full support for SystemVerilog. A
specific launcher is required for Verilator, since it isn't a standard SystemVerilog
simulator.


## Python entrypoint
- Launcher needs to know what to run
- It's expected that the entrypoint either deals with blocking functions or 
  ends by calling 'yield' in a loop

## Threading API (co-routines)
- Need something that runs when all co-routines are blocked (default co-routine?)
- 

## Blocking Datatypes
- semaphore
- mutex/condition
- mailbox
- fifo (?)

## Low-level simulator API
- advance API
- current time
- command-line arguments


# TODO
- Handle cases where the user doesn't supply arguments to @import_tas
  - https://stackoverflow.com/questions/7492068/python-class-decorator-arguments
- Have the user specify an entry-point to the launcher
  - Without an entry point, registration happens after the first BFM tries to initialize
  - Need to consider differences in environment to ensure that 
  - Need to consider a path forward to UVM to ensure that UVM behaves as expected
    - Possibly, we'll always want the user to provide the main hook, since this
      causes the user to import all packages that they need
    
- Specify the API the wrapper can expect to be provided by the launcher.
  - Maybe just pyhpi_launcher_init()
  - Actually, might want to redirect the 'init' hook back to the launcher
  - In some cases, we'll need to detect initialization based on the BFMs initializing
    - Example: In a DPI environment, having the user explicitly call 'init' isn't needed
    
