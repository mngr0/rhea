from myhdl import block, delay, instance, now


@block
def ClkDriver(clk, period=2):

    lowTime = int(period / 2)
    highTime = period - lowTime

    @instance
    def drive_clk():
        while True:
            yield delay(lowTime)
            #print("%s godown"% (now()))
            clk.next = 1
            yield delay(highTime)
            clk.next = 0
            #print("%s goup"% now())

    return drive_clk
