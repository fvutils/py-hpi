
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



