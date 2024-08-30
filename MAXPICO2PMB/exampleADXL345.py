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
