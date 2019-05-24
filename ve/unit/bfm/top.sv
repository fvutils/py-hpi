
module top(input clk);

task foo();
endtask

export "DPI-C" task foo;
// import "DPI-C" context task run_my_tb(int a);

initial begin
end

int count = 0;
wire[7:0]	data;
wire		req;
wire		ack;

simple_bfm u_bfm(.clk(clk), .req(req), .ack(ack), .data(data));

/*
always @(posedge clk) begin
  count <= count + 1;
  if ((count%10) == 0) begin
    run_my_tb(count);
  end
end
 */

endmodule

