upload: tb.bin
	sudo iceprog tb.bin

tb.bin: tb.txt
	icepack tb.txt tb.bin

tb.txt: tb.blif
	arachne-pnr -d 8k -p example-8k.pcf -o tb.txt tb.blif

tb.blif: spi_slave_pulsegen.v
	yosys -p "read_verilog spi_slave_pulsegen.v; synth_ice40 -blif tb.blif"

spi_slave_pulsegen.v: spi_slave_pulsegen.py
	python spi_slave_pulsegen.py

clean:
	rm tb.* *.v *.vcd *.pyc

test: spi_slave_pulsegen.py
	python spi_slave_pulsegen.py --test
