
module simple_bfm(
	input		clk,
	output		req,
	output[7:0]	data,
	input		ack);

	bit req_r = 0;

	assign req = req_r;

	task simple_bfm_req(int data);
		$display("req");
		req_r = 1;
	endtask
	export "DPI-C" task simple_bfm_req;

	import "DPI-C" context task simple_bfm_ack(int id);

	import "DPI-C" context function int simple_bfm_register(string path);

	always @(posedge clk) begin
		if (req) begin
			$display("--> ack");
			simple_bfm_ack(m_id);
			$display("<-- ack");
			req = 0;
		end
	end


	int m_id;
	initial begin
		m_id = simple_bfm_register($sformatf("%m"));
	end
		
endmodule
	
