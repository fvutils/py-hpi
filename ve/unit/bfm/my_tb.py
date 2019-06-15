import hpi
import simple_bfm
import sys

# my_bfm = simple_bfm()

dummy_sem = hpi.semaphore()

def thread_func_1():
  print("thread_func_1")
  my_bfm = hpi.rgy.bfm_list[0]
  for i in range(100000):
    my_bfm.xfer(i*2)
  print("thread1: Done")

def thread_func_2():
  print("thread_func_2")
  my_bfm = hpi.rgy.bfm_list[1]
  for i in range(100000):
    my_bfm.xfer(i)
  print("thread1: Done")

def lambda_accept(c):
  c()

@hpi.entry
def run_my_tb():
    print("run_my_tb - bfms: " + str(len(hpi.rgy.bfm_list)))

    with hpi.fork() as f:
      f.task(lambda: thread_func_1());
      f.task(lambda: thread_func_2());

    print("end of run_my_tb");

