
import hpi
from hpi import scheduler
import threading

t1_2_sem = hpi.semaphore()
t2_1_sem = hpi.semaphore()

def my_thread_1():
  global t1_2_sem
  global t2_1_sem
  print("--> my_thread_1")

  for i in range(2):
    print("--> T1: put")
    t1_2_sem.put(1)
    print("<-- T1: put")

    print("--> T1: get")
    t2_1_sem.get(1);
    print("<-- T1: get")

  print("<-- my_thread_1")

def my_thread_2():
  global t1_2_sem
  global t2_1_sem
  print("--> my_thread_2")

  for i in range(2):
    print("--> T2: get")
    t1_2_sem.get(1)
    print("<-- T2: get")

    print("--> T2: put")
    t2_1_sem.put(1);
    print("<-- T2: put")

  print("<-- my_thread_2")

def main_thread():
  with hpi.fork() as f:
    f.task(lambda: my_thread_1())
    f.task(lambda: my_thread_2())

    @hpi.branch(f)
    def b():
      print("inline thread 1")

    @hpi.branch(f)
    def b():
      print("inline thread 2")

hpi.scheduler.create_root_thread(main_thread)

for i in range(16):
  r = hpi.thread_yield()
  print("yield: " + str(i) + " " + str(r))

print("Done: " + str(len(hpi.scheduler.prv_active_thread_list)) + " " + str(threading.active_count()))


