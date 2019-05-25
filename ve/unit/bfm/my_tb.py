import hpi
import simple_bfm

# my_bfm = simple_bfm()

dummy_sem = hpi.semaphore()

def thread_func_1():
  print("thread_func_1")
  dummy_sem.get(1)

def thread_func_2():
  print("thread_func_2")
  dummy_sem.get(1)

@hpi.entry
def run_my_tb():
    print("run_my_tb");
    with hpi.fork() as f:
      f.task(lambda: thread_func_1());
      f.task(lambda: thread_func_2());

    print("end of run_my_tb");
    pass

