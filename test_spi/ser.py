
import myhdl
from myhdl import Signal, intbv, always, concat

#       serializer
#       ---------
#       |       |
# tx  >-+-------+-> bit_out
#       |       |
#       ---------


#TODO MSB/LSB
#shift << or >>
#concatenation in head or tail
  
#TODO CPHA/CPOL
#CPOL first or second edge
#CPHA idle state


@myhdl.block
def ser(
	# ~~~[Ports]~~~
	clock,	#
	tx,	#
	bit_out,#
	# ~~~[Parameters]~~~
	enable,
	size=8
):
	assert len(tx) == size
	# serialization regiester
	ser_reg = Signal(intbv(0)[size:])
	bitcnt = Signal(intbv(size-1, min=0, max=size+1))

	@always(clock.posedge)
	def serialization():
		if(enable == 1):
			if bitcnt == (size-1):
				bitcnt.next = 0
				ser_reg.next = (tx << 1) & 0xFF
				bit_out.next=tx[7]
			else:
				bit_out.next=ser_reg[7]
				ser_reg.next= (ser_reg << 1) & 0xFF
				bitcnt.next = bitcnt + 1
		else:
			ser_reg.next=0
			bitcnt.next = size-1
			bit_out.next=0

	return myhdl.instances()
