# py-HPI

The Python HDL Procedural Interface (py-HPI) implements a mechanism for Python scripts and
HDL (SystemVerilog and eventually Verilog, VHDL) to interact at the procedural level. 
This means that Python can call SystemVerilog tasks, and SystemVerilog can call
Python methods. Interacting at the procedural level enables support for a broader set of
execution environments (simulators), supports a broader range of integration styles, 
and provides higher performance than does integration at the signal level. 

# Theory of Operations

- General structure

## BFMs

There are two pieces to a pyHPI BFM: the Python side and the HDL side. The Python side
consists of a Python class with specific 
[decorators](https://realpython.com/primer-on-python-decorators/) to identify key 
elements of the BFM class. The HDL side consists of SystemVerilog source 
(or Verilog/VHDL in the future) that translates between procedure calls to 
signal-level activity, and vice versa.

### Python
The Python side of a pyHPI BFM is implemented with a Python class. Three decorators
are used to identify key elements within the BFM:
- The BFM itself (@hpi.bfm)
- Import methods (@hpi.import_task) -- methods provided by Python and called by the HDL
- Export methods (@hpi.export_task) -- methods provided by the HDL and called by Python

Here's a short example of a BFM:

```python
@hpi.bfm
class simple_bfm():
    
  def __init__(self):
    self.ack_sem = hpi.semaphore()

  def xfer(self,data):
    self.req(data)
    self.ack_sem.get(1)

  @hpi.export_task("i")
  def req(self, data : int):
    pass

  @hpi.import_task()
  def ack(self):
    self.ack_sem.put(1)
```

#### Parameter-Type Annotations
Python is a dynamically typed language. However, it is important to know the precise
type of parameters being passed to/from HDL. This information is provided via the
argument passed to the _import_task_ and _export_task_ decorators. The type of 
each method parameter is specified with one or two characters:

- **s** - String
- **i** - Signed 32-bit integer parameter
- **iu** - Unsigned 32-bit integer parameter
- **l** - Signed 64-bit integer parameter
- **lu** - Unsigned 64-bit integer parameter


- Python Side
  - Registration of class
  - Registration of methods

### HDL

#### SystemVerilog  
The SystemVerilog 
- SystemVerilog side
  - Registration of each BFM instance
  - Export tasks (note naming convention)
  - Import tasks

## Python testbench
- Entry point
  - Runs in a thread
  - Simulation stops when it exits (?)
- Access to plusargs  
- BFM registry
- Threading API
  - Thread create
  - Semaphore (semaphore)
  - Objection

## Simulator Support (Launcher)

### Standard SystemVerilog DPI Simulator (eg Modelsim)

### Verilator


## Testbench Wrapper

## Running Simulation

### Common options
- +hpi.entry=<function>
- +hpi.load=<module>

### Standard SystemVerilog DPI Simulator

### Verilator


## Wrapper Generation

# Launcher
- Command-line arguments
- Specification of python paths
- Loading of Python modules
- Entry point (?) 

