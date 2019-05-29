#****************************************************************************
#* scheduler.py
#****************************************************************************
'''
Created on May 25, 2019

@author: ballance
'''
import threading
from threading import Lock
from threading import Condition

prv_active_mutex = Lock()
prv_active_thread_started = False
prv_active_thread_start_cond = threading.Condition(prv_active_mutex)
prv_active_thread = None
prv_active_thread_list = []
prv_blocked_thread_list = []

class SimThreadData():
    def __init__(self):
        self.running = False
        self.run_sem = threading.Semaphore(0)

class semaphore:
    def __init__(self, init=0):
        self.count = init
        self.thread = None
        
    def put(self, count=1):
        self.count += count
        
        if self.thread != None:
            self.thread.unblock()
    
    def get(self, count=1):
        global prv_active_thread
        global prv_active_mutex

        prv_active_mutex.acquire()        
        self.thread = prv_active_thread
        prv_active_mutex.release()
        
        while self.count < count:
            self.thread.block()

        self.thread = None
        self.count -= count
    
class ThreadGroup:
    
    def __init__(self, threads=[]):
        self.threads = threads;
        self.sem = semaphore()
        
        for t in threads:
            t.add_join_listener(self)
            
    def add(self,thread):
        self.threads.append(thread)
        thread.add_join_listener(self)
            
    def join_all(self):
#        print("--> join_all.get()")
        self.sem.get(len(self.threads))
#        print("<-- join_all.get()")
        
    def join_any(self):
        self.sem.get(1);
       
    def thread_ended(self, t):
#        print("--> thread_ended")
        self.sem.put(1);
#        print("<-- thread_ended")
        
class SimThread(threading.Thread,SimThreadData):
    
    def __init__(self, func):
        threading.Thread.__init__(self)
        SimThreadData.__init__(self)
        # Make SimThreads daemon threads to allow Python to shut down
        # with threads still active
        self.daemon = True
        self.join_listeners = []
        self.func = func
        self.run_mutex = Lock()
        self.run_cond = Condition(self.run_mutex)
        self.suspend_mutex = Lock()
        self.suspend_cond = Condition(self.suspend_mutex)
        self.running = False
        self.alive = False
        
    def run(self):
        self.running = True
        self.alive = True
        
#        print("--> run")
        prv_active_mutex.acquire()
        prv_active_thread_list.append(self)
        prv_active_thread_start_cond.notify()
        prv_active_mutex.release()
   
#        print("--> Wait to run")
        self.thread_yield()
#        print("<-- Wait to run")
        
#        print("--> calling function " + str(self.func))
        self.func()
#        print("<-- calling function")
#        print("<-- run")
        
#        print("--> notify listeners")
        for l in self.join_listeners:
            l.thread_ended(self)
#        print("<-- notify listeners")
        
        # TODO: cleanup after thread
        # Note: we know we're the active thread 
        # because we're running
#        print("--> final notification")
        self.running = False
        self.alive = False
        self.suspend_mutex.acquire()
        self.suspend_cond.notify()
        self.suspend_mutex.release()
#        print("<-- final notification")
        
#        print("Note: thread complete " + str(self))

    def add_join_listener(self, l):
        self.join_listeners.append(l)
        
    def block(self):
#        print("--> block " + str(self))
        self.running = False
        self.suspend_mutex.acquire()
        self.suspend_cond.notify()
        self.suspend_mutex.release()
        
        self.run_mutex.acquire()
        self.run_cond.wait()
        self.run_mutex.release()
        
#        print("<-- block " + str(self))
        

    def unblock(self):
#        print("--> unblock " + str(self))
        global prv_active_thread_list
        global prv_active_mutex
        
        if self.running == False:
            self.running = True
       
            prv_active_mutex.acquire()
            prv_active_thread_list.append(self)
            prv_active_mutex.release()
            
#        print("<-- unblock " + str(self))
        
    def thread_run(self):
        global prv_active_thread
        global prv_active_mutex
        prv_active_mutex.acquire()
        prv_active_thread = self
        prv_active_mutex.release()
        
#        print("prv_active_thread: " + str(prv_active_thread))
        
        self.run_mutex.acquire()
        self.run_cond.notify()
        self.run_mutex.release()
       
        # wait for thread to suspend or exit
        self.suspend_mutex.acquire()
        self.suspend_cond.wait()
        self.suspend_mutex.release()
       
        return self.running

    def thread_yield(self):
#        print("--> thread_yield")
        self.run_mutex.acquire()
        self.run_cond.wait()
        self.run_mutex.release()
#        print("<-- thread_yield")
        
def thread_active():
    return prv_active_thread

def thread_yield():
    global prv_active_mutex
    global prv_active_thread
    global prv_active_thread_list
    yielded = False
    
#    print("thread_yield: len=" + str(len(prv_active_thread_list)))
    
    if len(prv_active_thread_list) != 0:
            
        # Suspend ourselves and let another thread run
        prv_active_mutex.acquire()
            
        prv_active_thread = prv_active_thread_list.pop(0);
        
#        print("active thread: " + str(prv_active_thread))
        prv_active_mutex.release()

#        print("--> thread_run")        
        running = prv_active_thread.thread_run()
#        print("<-- thread_run")        
      
        if running == True:
            # Put thread back on the running list
#            print("-- is_running")
            prv_active_thread_list.append(prv_active_thread)
            
        yielded = True

    # Active thread is only valid during thread execution
    prv_active_thread = None
    
    return yielded

def int_thread_yield():
#    print("--> int_thread_yield")
    
    for i in range(1000):
        if thread_yield() == False:
#            print("int_thread_yield: quit after " + str(i))
            break
    
#    print("<-- int_thread_yield")
    
def thread_block():
    pass

def thread_create(func):
    global prv_active_mutex
    global prv_active_thread_start_cond
    # TODO: handle startup synchronization
    
    prv_active_mutex.acquire()
    if prv_active_thread == None:
        prv_active_mutex.release()
        raise Exception("Attempting to create a sim thread outside a simulation thread")
    
    t = SimThread(func)
    t.start()
#    print("--> wait for thread to start")
    prv_active_thread_start_cond.wait()
#    print("<-- wait for thread to start")
    prv_active_mutex.release()
    
    return t

def create_root_thread(func):
    t = SimThread(func)
    # TODO: handle startup synchronization
    prv_active_mutex.acquire()
    t.start()
#    print("--> wait for thread to start")
    prv_active_thread_start_cond.wait()
#    print("<-- wait for thread to start")
    prv_active_mutex.release()
    
    return t

class branch:
    
    def __init__(self, f):
        self.f = f
        
    def __call__(self,func):
        self.f.task(func)
        
class fork():
  
    def __init__(self, jtype="join"):
        self.jtype = jtype
        self.callables = []
        
        if jtype not in ["join", "join_none", "join_one"]:
            raise Exception("Join type \"" + jtype + "\" unrecognized")
       
    def __enter__(self):
        return self
    
    def __exit__(self, t, v, tb):
        threads = []
        for c in self.callables:
            threads.append(thread_create(c))

        if self.jtype != "join_none":
            tg = ThreadGroup(threads)
            if self.jtype == "join":
                tg.join_all()
            else: 
                tg.join_one()

    def task(self, func):
        self.callables.append(func)
    
    