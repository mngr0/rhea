import sys
import os
sys.path.append( os.path.abspath("../../..") )


import myhdl
from myhdl import (Signal, intbv, instance, always_comb, delay, always,
                   StopSimulation, block)

from rhea.system import Global, Clock, Reset, FIFOBus, Signals
from rhea.cores.spi import SPIBus, spi_slave_fifo_async, spi_slave_fifo
from rhea.utils.test import run_testbench, tb_default_args, tb_args
from ser import ser
from ClkDriver import ClkDriver
from pulsegen import pulsegen

sck = Signal(False)
mosi = Signal(False)
miso  = Signal(False)
cs  = Signal(True)
leds = Signal(intbv(0)[8:])
out  = Signal(True)

clock  = Signal(False)
clk_div = Signal(False)

tx = Signal(intbv(0)[8:])
#rx = Signal(intbv(0)[8:])
enable = Signal (False)
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
def recv_to_led(clock, fifobus, leds,out):
    reading=  Signal (False)
    pulse_in = Signal(intbv(0)[8:])
    clk_div = Signal(False)
    div = divisor (clock, clk_div, 100)
    plsgen = pulsegen(clock=clk_div, frequence=pulse_in, duration=10, out_pulse = out)

    @always(clock.posedge)
    def go_to_led():
        if reading :
            leds.next = fifobus.read_data
            pulse_in.next = fifobus.read_data
            fifobus.read.next = False
            reading.next = False
        else:
            if not fifobus.empty :
                fifobus.read.next = True
                reading.next = True

    return go_to_led, plsgen, div



@block
def spi_slave_led(clock, sck, mosi, miso, cs, leds ,out):
    glbl = Global(clock)
    spibus = SPIBus(sck=sck, mosi=mosi, miso=miso, ss=cs)
    fifobus = FIFOBus()
    div = divisor (clock, clk_div, 10)
    fifobus.write_clock=clock
    fifobus.read_clock=clock

    rtl = recv_to_led(clock, fifobus, leds,out)
    tbdut = spi_slave_fifo(glbl, spibus, fifobus)

    @always_comb
    def map():
        spibus.csn.next = cs

    return myhdl.instances()


@block
def test_spi_led(clock, sck, mosi, miso, cs, leds,out):
    clkdrv = ClkDriver(clock,period=10)
    ssled = spi_slave_led(clock, sck, mosi, miso, cs, leds,out)
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

if "--test" in str(sys.argv):
	do_test=True
else:
    do_test=False

if do_test:
    tr = test_spi_led(clock, sck, mosi,miso, cs, leds,out)
    tr.config_sim(trace=True)
    tr.run_sim(10000)
else:
    tr = spi_slave_led(clock, sck, mosi,miso, cs, leds,out)
    tr.convert('Verilog',initial_values=True)
