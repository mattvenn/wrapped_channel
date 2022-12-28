import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clock, 25, units="ns") # 40M
    cocotb.fork(clock.start())
        
    dut.RSTB = 0
    dut.power1 = 0
    dut.power2 = 0
    dut.power3 = 0
    dut.power4 = 0

    dut.sample = 0

    await ClockCycles(dut.clock, 8)
    dut.power1 = 1
    await ClockCycles(dut.clock, 8)
    dut.power2 = 1
    await ClockCycles(dut.clock, 8)
    dut.power3 = 1
    await ClockCycles(dut.clock, 8)
    dut.power4 = 1

    await ClockCycles(dut.clock, 80)
    dut.RSTB = 1

    # wait with a timeout for the project to become active
    await with_timeout(RisingEdge(dut.uut.mprj.wrapped_channel_1.active), 1500, 'us')

    # wait for channel module to come out of reset
    await with_timeout(FallingEdge(dut.uut.mprj.wrapped_channel_1.gps_channel0.reset), 1500, 'us')

    # wait for LO NCO to be turned on
    await with_timeout(RisingEdge(dut.uut.mprj.wrapped_channel_1.gps_channel0.lo_nco_enable), 3000, 'us')

    # wait for CA generator to be turned on
    await with_timeout(RisingEdge(dut.uut.mprj.wrapped_channel_1.gps_channel0.ca_gen_enable), 3000, 'us')

    # wait for some chips to be generated by the two NCOs
    await ClockCycles(dut.clock, 5000)

    # assert something to terminate the test
    # TODO(adrianwong): Replace with some checks on LO NCO and CA gen accuracy
    # TODO(adrianwong): Currently a visual check on gtkwave that:
    #                    the two NCOs are moving at different frequencies
    #                    C/A code is chipping out
    #                    prompt_i I/O pad has something that looks like a mixed signal

#    assert(0 == 0)
