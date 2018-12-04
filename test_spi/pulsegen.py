from myhdl import Signal, intbv, always, always_comb, block, now

@block
def pulsegen(
	# ~~~[Ports]~~~
	clock,		# input  : clock
	frequence,	# input  : one pulse will start every frequence clock cycles
	duration,	# input  : every pulse will last duration clock cycles
	out_pulse,	# output : the output with the pulse
	# ~~~[Parameters]~~~
	cnt_max = 10000000
):
	pulse_mem = Signal(intbv(0)[1:0])
	clk_cnt = Signal(intbv(0, min=0, max=cnt_max))

	@always(clock.posedge)
	def beh_strobe():
		#print ("%s posedge "%(now()))
		if clk_cnt >= frequence:
			pulse_mem.next = 0
			clk_cnt.next = 0
		else:
			if clk_cnt >= duration:
				pulse_mem.next = 0
				clk_cnt.next = clk_cnt + 1
			else:
				pulse_mem.next = 1
				clk_cnt.next = clk_cnt + 1

	@always_comb
	def beh_map_output():
		out_pulse.next = pulse_mem

	return beh_strobe, beh_map_output
