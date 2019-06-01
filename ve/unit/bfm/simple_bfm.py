
import hpi
from hpi.rgy import bfm_wrapper_type

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

simple_bfm_sv = '''
module simple_bfm(
    input        clk,
    output reg    req_o,
    output reg [7:0] data,
    input        ack);

    bit req_r = 0;
    bit[7:0] data_r = 0;

    always @(posedge clk) begin
        req_o <= req_r;
        data <= data_r;
    end

    task simple_bfm_req(int data);
        req_r = 1;
        data_r = data;
    endtask
    export "DPI-C" task simple_bfm_req;

    import "DPI-C" context task simple_bfm_ack(int id);

    import "DPI-C" context function int simple_bfm_register(string path);

    always @(posedge clk) begin
        if (req_o && ack) begin
            // Remember that new requests can 
            // occur as a side effect of the ack
            req_r = 0;
            simple_bfm_ack(m_id);
        end
    end

    int m_id;
    initial begin
        m_id = simple_bfm_register($sformatf("%m"));
    end
        
endmodule
'''
     
# BFM Template registration
simple_bfm.bfm_wrappers = {
    bfm_wrapper_type.SV_DPI : simple_bfm_sv
}