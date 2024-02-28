################################################################################
# Copyright (C) 2024 Analog Devices, Inc.
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
from MAXPICO2PMB import MAXPICO2PMB
import time

#ADXL345 Device Constants
ADXL345_ADDR    = 0x1D
ADXL345_DEVID   = 0xE5
REG_DEVID       = 0x00
REG_PWRCTRL     = 0x2D
REG_DATAFMT     = 0x31
REG_DATAX0      = 0x32
DATA_REG_COUNT  = 6

def ConvertAndPrintValues(regValues, range):
    '''
    Helper for printing out acceleration values in G's.

    Inputs
        regValues - List of register values read from the device. DATAX0-DATAZ1
        range - Scale factor in G's
    '''
    x = int.from_bytes(regValues[0:2], 'little', signed=True)
    y = int.from_bytes(regValues[2:4], 'little', signed=True)
    z = int.from_bytes(regValues[4:6], 'little', signed=True)
    #Data is signed 10-bit
    print('+/-{:d}g - X:{:f}, Y:{:f}, Z:{:f}'.format(
            range, (x / 512) * range, (y / 512) * range, (z / 512) * range))


#Entry point for the test script
if __name__ == '__main__':
    #Find the MAXPICO2PMB
    print('Looking for a MAXPICO2PMB')
    iface = MAXPICO2PMB()
    if iface.isConnected():
        print('Success!')
    else:
        print('Failed to find MAXPICO2PMB')
        exit()

    print(iface.getVersionString())

    #Check the device is present with valid DEV_ID
    devId = iface.readRegister(ADXL345_ADDR, REG_DEVID)
    if devId != ADXL345_DEVID:
        print('Invalid DEV ID {:02X}'.format(devId))
    else:
        print('Valid Dev ID: {:02X}'.format(devId))

    #Enable measurement mode
    iface.writeRegister(ADXL345_ADDR, REG_PWRCTRL, 0x8)

    # Loop an arbitrary number of times to test
    for i in range(10):
        #Test 2g Range, 10-bit mode
        iface.writeRegister(ADXL345_ADDR, REG_DATAFMT, 0x00)
        data = iface.readRegisters(ADXL345_ADDR, REG_DATAX0, DATA_REG_COUNT)
        ConvertAndPrintValues(data, 2)

        time.sleep(0.5)

        #Test 4g Range, 10-bit mode
        iface.writeRegister(ADXL345_ADDR, REG_DATAFMT, 0x01)
        data = iface.readRegisters(ADXL345_ADDR, REG_DATAX0, DATA_REG_COUNT)
        ConvertAndPrintValues(data, 4)

        time.sleep(0.5)

        #Test 8g Range, 10-bit mode
        iface.writeRegister(ADXL345_ADDR, REG_DATAFMT, 0x02)
        data = iface.readRegisters(ADXL345_ADDR, REG_DATAX0, DATA_REG_COUNT)
        ConvertAndPrintValues(data, 8)

        time.sleep(0.5)

        #Test 16g Range, 10-bit mode
        iface.writeRegister(ADXL345_ADDR, REG_DATAFMT, 0x03)
        data = iface.readRegisters(ADXL345_ADDR, REG_DATAX0, DATA_REG_COUNT)
        ConvertAndPrintValues(data, 16)

        time.sleep(2)

    #Clean up the interface
    del iface
