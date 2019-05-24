
import hpi

print("Hello from simple_bfm")

@hpi.bfm
class simple_bfm():

  def __init__(self):
    pass

  @hpi.export_task("i")
  def req(self, data : int):
    pass

  @hpi.import_task()
  def ack(self):
    print("ack")


