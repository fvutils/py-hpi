
import hpi

print("Hello from simple_bfm")

@hpi.bfm
class simple_bfm():

  def __init__(self):
    self.ack_sem = hpi.semaphore()
    pass

  def xfer(self,data):
    self.req(data)
    print("--> ack_sem.get()")
    self.ack_sem.get(1)
    print("<-- ack_sem.get()")

  @hpi.export_task("i")
  def req(self, data : int):
    pass

  @hpi.import_task()
  def ack(self):
    print("ack")
    print("--> ack_sem.put()")
    self.ack_sem.put(1)
    print("<-- ack_sem.put()")


