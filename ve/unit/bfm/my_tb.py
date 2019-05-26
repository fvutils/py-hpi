import hpi
import simple_bfm
import sys

# my_bfm = simple_bfm()

dummy_sem = hpi.semaphore()

def thread_func_1():
  print("thread_func_1")
  my_bfm = hpi.rgy.bfm_list[0]
  my_bfm.xfer(10)
  my_bfm.xfer(20)
  my_bfm.xfer(30)
  my_bfm.xfer(40)

def thread_func_2():
  print("thread_func_2")
  my_bfm = hpi.rgy.bfm_list[1]
  my_bfm.xfer(110)
  my_bfm.xfer(120)
  my_bfm.xfer(130)
  my_bfm.xfer(140)

@hpi.entry
def run_my_tb():
    print("run_my_tb - bfms: " + str(len(hpi.rgy.bfm_list)))

    with hpi.fork() as f:
      f.task(lambda: thread_func_1());
      f.task(lambda: thread_func_2());

    print("end of run_my_tb");
    pass

