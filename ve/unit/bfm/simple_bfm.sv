
module simple_bfm(
	input		clk,
	output reg	req_o,
	output reg [7:0] data,
	input		ack);

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
//			req_o <= 0;
		end
	end


	int m_id;
	initial begin
		m_id = simple_bfm_register($sformatf("%m"));
	end
		
endmodule
	
