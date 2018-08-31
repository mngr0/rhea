upload: tb.bin
	sudo iceprog tb.bin

tb.bin: tb.txt
	icepack tb.txt tb.bin

tb.txt: tb.blif
	arachne-pnr -d 8k -p example-8k.pcf -o tb.txt tb.blif

tb.blif: spi_slave_led.v
	yosys -p "read_verilog spi_slave_led.v; synth_ice40 -blif tb.blif"

spi_slave_led.v: spi_slave_led.py
	python spi_slave_led.py

clean:
	rm tb.* *.v *.vcd *.pyc

