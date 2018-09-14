import sys
import os
sys.path.append( os.path.abspath("../../..") )


import myhdl
from myhdl import (Signal, intbv, instance, always_comb, delay, always,
                   StopSimulation, block)

from rhea.system import Global, Clock, Reset, FIFOBus, Signals
from rhea.cores.spi import SPIBus, spi_slave_fifo
from rhea.utils.test import run_testbench, tb_default_args, tb_args
from ser import ser
from ClkDriver import ClkDriver

sck = Signal(False)
mosi = Signal(False)
miso  = Signal(False)
cs  = Signal(True)
leds = Signal(intbv(0)[8:])
clock  = Signal(False)
clk_div = Signal(False)

tx = Signal(intbv(0)[8:])
#rx = Signal(intbv(0)[8:])
enable = Signal (0)
#reset = ResetSignal(False)

@block
def divisor(
	# ~~~[Ports]~~~
	clk_in,		# input  : clock
	clk_out,	# output  : one pulse will start every frequence clock cycles
	# ~~~[Parameters]~~~
	division = 100
):
	div_mem = Signal(intbv(0)[1:0])
	clk_cnt = Signal(intbv(0, min=0, max=division))

	@always(clk_in.posedge)
	def beh_strobe():
		if clk_cnt >= division-1:
			div_mem.next = not div_mem
			clk_cnt.next = 0
		else:
			clk_cnt.next = clk_cnt + 1

	@always_comb
	def beh_map_output():
		clk_out.next = div_mem

	return beh_strobe, beh_map_output


@block
def recv_to_led(clock, fifobus, leds):
    reading=  Signal (False)

    @always(clock.posedge)
    def go_to_led():
        if reading :
            leds.next = fifobus.read_data
            fifobus.read.next = False
            reading.next = False
        else:
            if not fifobus.empty :
                fifobus.read.next = True
                reading.next = True

    return go_to_led



@block
def spi_slave_led(clock, sck, mosi, miso, cs, leds):
    glbl = Global(clock)
    spibus = SPIBus(sck=sck, mosi=mosi, miso=miso, ss=cs)
    fifobus = FIFOBus()
    div = divisor (clock, clk_div, 9)
    rtl = recv_to_led(clk_div, fifobus, leds)
    tbdut = spi_slave_fifo(glbl, spibus, fifobus)

    @always_comb
    def map():
        spibus.csn.next = cs

    return myhdl.instances()


@block
def test_spi_led(clock, sck, mosi, miso, cs, leds):
    clkdrv = ClkDriver(clock,period=10)
    ssled = spi_slave_led(clock, sck, mosi, miso, cs, leds)
    ts = ser (clock, tx, mosi, enable)

    @always_comb
    def map():
        sck.next = clock
        

    @instance
    def tbstim():
        yield delay(15)
        enable.next=1
        tx.next=42
        cs.next=0
        yield delay(90)
        enable.next=0
        cs.next=1
        #assert rx == 42

        yield delay(15)
        enable.next=1
        tx.next=98
        yield delay(70)
        tx.next=23
        yield delay(20)		
        #assert rx == 98
        yield delay(90)
        #assert rx == 23
        enable.next=0
        yield delay(100)


    return myhdl.instances()



tr = test_spi_led(clock, sck, mosi,miso, cs, leds)
tr.config_sim(trace=True)
tr.run_sim(1000)
#tr.convert('Verilog',initial_values=True)