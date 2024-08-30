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
import serial
from serial.tools import list_ports as ports
import time

class MAXPICO2PMB:
    '''
    MAXPICO2PMB - Simple class for communicating with a MAXPICO2PMB for
                  I2C communications. Will automatically detect the device
                  upon creation.  Note: The MAXPICO2PMB instance must be
                  cleared when finished to correctly close out the serial port
    '''
    #Initializes the class instance
    def __init__(self, explicitPort = None):
        '''
        Class constructors.  Automatically searches for a MAXPICO2PMB device
        among all of the comm ports.  If explicitPort is passed, only that port
        will be checked

        explicitPort - Force a specific COM port
        '''
        self.__portConn = None

        if explicitPort == None:
            availPorts = [port.device for port in ports.comports()]
        else:
            availPorts = [explicitPort]

        for port in availPorts:
            try:
                s = serial.Serial(port, 115200, timeout=1.0)
                #Sleep a tick, then flush the read just in case anything lingering
                time.sleep(0.5)
                s.read_all()

                #Use the G 2 command to get the Version string
                s.write(b'G 2\r\n')
                id_str = str(s.readline(), 'utf-8')

                if(id_str.startswith('MAXPICO2PMB')):
                    self.__portConn = s
                    self.__versionStr = id_str.strip()
                    print('Port {} appears to be a MAXPICO2PMB'.format(s.name))
                    return
                else:
                    s.close()
            except:
                print('Error working with {}'.format(port))

        print('Did not find a MAXPICO2PMB')


    #Cleans up the class
    def __del__(self):
        '''
        Class destructor. Close out the comm port
        '''
        if not self.__portConn is None:
            self.__portConn.close()
            self.__portConn = None


    #Checks if the MAXPICO2PMB is connected
    def isConnected(self):
        '''
        Returns if the COM port is active and connected
        '''
        return (not self.__portConn is None)


    #Gets the version string provided by the MAXPICO2PMB
    def getVersionString(self):
        '''
        Returns back the version string provided by the device

        Outputs
            Device version string
        '''
        return self.__versionStr


    #Writes a single device register
    def writeRegister(self, busAddr, regAddr, value):
        '''
        Writes a register on the I2C device

        Inputs
            busAddr - 7-bit I2C Address
            regAddr - 1-byte Device Address
            value   - 1-byte value to write
        '''
        self.writeRegisters(busAddr, regAddr, [value])


    #Writes consecutive registers of the device
    def writeRegisters(self, busAddr, regAddr, values):
        '''
        Writes consecutive registers on the I2C device

        Inputs
            busAddr - 7-bit I2C Address
            regAddr - 1-byte Device Address
            values   - List of values to write. Length is number of registers
        '''
        if(len(values) < 1):
            raise Exception('Must provide at least 1 value')

        #Device wants 8-bit I2C address with LSB 0
        ctrlStr = 'w {:02X} {:02X} '.format(busAddr << 1, regAddr)
        for v in values:
            ctrlStr += '{:02X}'.format(v)
        ctrlStr += '\r\n'

        self.__portConn.write(ctrlStr.encode('utf-8'))
        result = str(self.__portConn.readline(), 'utf-8')
        if( not result.startswith('ack')):
            raise Exception('Bus Nack Exception')


    #Reads a single device register
    def readRegister(self, busAddr, regAddr):
        '''
        Reads a register on the I2C device

        Inputs
            busAddr - 7-bit I2C Address
            regAddr - 1-byte Device Address

        Outputs
            Value read
        '''
        return self.readRegisters(busAddr, regAddr, 1)[0]

    #Reads consecutive registers on the device
    def readRegisters(self, busAddr, regAddr, count):
        '''
        Reads consecutive registers on the I2C device

        Inputs
            busAddr - 7-bit I2C Address
            regAddr - 1-byte Device Address
            count   - Number of registers to read

        Outputs
            List of register values read. Len will equal count
        '''
        if(count < 1):
            raise Exception('Register read must be at least 1')

        #Device wants 8-bit I2C address with LSB 0
        ctrlStr = 'r {:02X} {:02X} {:02X}\r\n'.format(busAddr << 1, regAddr, count)
        self.__portConn.write(ctrlStr.encode('utf-8'))

        values = []
        for i in range(count):
            result = str(self.__portConn.readline(), 'utf-8')
            if result.startswith('nack'):
                raise Exception('Bus Nack Exception')
            else:
                values.append(int(result, 16))
        return values


#Simple catch for running directly.  Looks for a device then exits
if __name__ == '__main__':
    print('Looking for a MAXPICO2PMB')
    l = MAXPICO2PMB()
    if l.isConnected():
        print('Success!')
    else:
        print('Failed to find MAXPICO2PMB')

    print(l.getVersionString())
    del l
