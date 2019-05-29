
import hpi

@hpi.bfm
class simple_bfm():

  def __init__(self):
    self.ack_sem = hpi.semaphore()
    pass

  def xfer(self,data):
    self.req(data)
    self.ack_sem.get(1)

  @hpi.export_task("i")
  def req(self, data : int):
    pass

  @hpi.import_task()
  def ack(self):
    self.ack_sem.put(1)


