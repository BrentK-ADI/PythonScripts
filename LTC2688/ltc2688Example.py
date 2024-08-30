###
# Copyright © 2024 by Analog Devices, Inc.  All rights reserved.
#
# This software is proprietary to Analog Devices, Inc. and its licensors.
#
# This software is provided on an “as is” basis without any representations,
# warranties, guarantees or liability of any kind.
#
# Use of the software is subject to the terms and conditions of the
# Clear BSD License ( https://spdx.org/licenses/BSD-3-Clause-Clear.html ).
###
from linduinoSPI import linduinoSPI
from ltc2688 import ltc2688
import time

def ltc2688Example():
    #find the DC590 or DC2026 connection
    ctrl = linduinoSPI();

    #Didn't find anything, return
    if not ctrl.isConnected():
        print('Serial connection not found');
        return

    # Select the correct Device type and bit depth for correct operation
    chip = ltc2688(ctrl, ltc2688.DEVICE_LTC2688, ltc2688.DEPTH_16_BIT)

    #For this example, Ch0 is 0-5V, and Ch1 is 0-10V
    chip.setSpan(0, ltc2688.SPAN_0_5V);
    chip.setSpan(1, ltc2688.SPAN_0_10V);

    valCh0 = 0;
    valCh1 = 0;

    #Loop an arbitrary number of times
    for i in range(2000):
        # Ch0 is a square wave
        if(i%2 == 0):
            valCh0 = 0xFFFF
        else:
            valCh0 = 0;

        # Ch1 is a ramp
        valCh1 = valCh1 + 0x100
        if( valCh1 >= 0xFFFF ):
            valCh1 = 0

        # Update the channels
        chip.setChannelCode(0, valCh0)
        chip.setChannelCode(1, valCh1)
        chip.updateAll()

        time.sleep(0.01)
    #clean up the serial port
    del ctrl


if __name__ == '__main__':
    ltc2688Example()
