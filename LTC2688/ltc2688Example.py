################################################################################
# Copyright (C) 2023 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  - Neither the name of Analog Devices, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#  - The use of this software may or may not infringe the patent rights
#    of one or more patent holders.  This license does not release you
#    from the requirement that you obtain separate licenses from these
#    patent holders to use this software.
#  - Use of the software either in source or binary form, must be run
#    on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT,
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, INTELLECTUAL PROPERTY RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################
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
