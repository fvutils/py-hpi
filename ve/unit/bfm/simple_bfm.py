
import hpi

print("Hello from simple_bfm")

@hpi.bfm
class simple_bfm():

  def __init__(self):
    self.ack_sem = hpi.semaphore()
    pass

  @hpi.export_task("i")
  def req(self, data : int):
    self.ack_sem.get(1)
    pass

  @hpi.import_task()
  def ack(self):
    print("ack")
    self.ack_sem.put(1)


