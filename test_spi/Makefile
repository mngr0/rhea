upload: tb.bin
	sudo iceprog tb.bin

tb.bin: tb.txt
	icepack tb.txt tb.bin

tb.txt: tb.blif
	arachne-pnr -d 8k -p example-8k.pcf -o tb.txt tb.blif

pulse: spi_slave_pulsegen.v
	yosys -p "read_verilog spi_slave_pulsegen.v; synth_ice40 -blif tb.blif"

led: spi_slave_led.v
	yosys -p "read_verilog spi_slave_led.v; synth_ice40 -blif tb.blif"

spi_slave_led.v: spi_slave_led.py
	python spi_slave_led.py

spi_slave_pulsegen.v: spi_slave_pulsegen.py
	python spi_slave_pulsegen.py

clean:
	rm tb.* *.v *.vcd *.pyc

test-led: spi_slave_led.py
	python spi_slave_led.py --test

test-pulse: spi_slave_pulsegen.py
	python spi_slave_pulsegen.py --test
