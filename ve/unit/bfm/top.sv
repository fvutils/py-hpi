
module top(input clk);

`ifdef HAVE_HDL_CLOCKGEN
reg clk_r = 0;
initial begin
  forever begin
    #10ns;
    clk_r <= ~clk_r;
  end
end
assign clk = clk_r;
`endif

wire[7:0]	data_1;
wire		req_1;
wire		ack_1;
reg		req_r_1 = 0;
wire[7:0]	data_2;
wire		req_2;
wire		ack_2;
reg		req_r_2 = 0;

always @(posedge clk) begin
	req_r_1 <= req_1;
	req_r_2 <= req_2;
end

assign ack_1 = req_r_1;
assign ack_2 = req_r_2;

always @(posedge clk) begin
  if (req_1 && ack_1) begin
    $display("ack_1=%0d data_1=%0d", ack_1, data_1);
  end
  if (req_2 && ack_2) begin
    $display("ack_2=%0d data_2=%0d", ack_2, data_2);
  end
end


simple_bfm u_bfm_1(.clk(clk), .req_o(req_1), .ack(ack_1), .data(data_1));
simple_bfm u_bfm_2(.clk(clk), .req_o(req_2), .ack(ack_2), .data(data_2));

endmodule

