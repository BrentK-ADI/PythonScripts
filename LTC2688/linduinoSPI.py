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
import string
from serial.tools import list_ports as ports
import time

class linduinoSPI:
    '''
    linduinoSPI - Simple class for communicating with a DC590B or DC2026 for
                  SPI communications. Will automatically detect the device
                  upon creation.  Note: The linduinoSPI instance must be
                  cleared when finished to correctly close out the serial port
    '''
    #Initializes the class instance
    def __init__(self, explicitPort = None):
        '''
        Class constructors.  Automatically searches for a Linduino devices among
        all of the comm ports.  If explicitPort is passed, only that port will
        be checked

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
                time.sleep(2)
                s.read_all()
                s.write(b'i')
                id_str = s.readline()

                if((len(id_str) > 24) and (id_str[20:25] == b'DC590')):
                    self.__portConn = s
                    print('Port {} appears to be a DC590 or Linduino'.format(s.name))
                    return
                else:
                    s.close()
            except:
                print('Error working with {}'.format(port))

        print('Did not find a DC590 or Linduino')


    #Cleans up the class
    def __del__(self):
        '''
        Class destructor. Close out the comm port
        '''
        if not self.__portConn is None:
            self.__portConn.close()
            self.__portConn = None

    #Checks if the Linduino is connected
    def isConnected(self):
        '''
        Returns if the COM port is active and connected
        '''
        return (not self.__portConn is None)


    def writeRead(self, data):
        '''
        writeRead - Performs a SPI write and read operation. The data passed in
                    should be an array of bytes to transmit. The return array
                    will be of equal length with the received data
         Inputs
           data - Array of bytes to transmit

         Outputs
           array of bytes received. Same length as data input
        '''
        retDat = [0]*len(data)
        ctrlStr = b'x'  #CS Low
        for byte in data:
            #Append all bytes with T for transaction, then ASCII hex
            ctrlStr += 'T{:02X}'.format(byte).encode()

        ctrlStr += b'XZ' #CS High and a new line
        self.__portConn.write(ctrlStr)

        #The Linduino sometimes puts escape characters (\x) in front of data and
        #python has a hard time handling it.  Simple generator to strip out non
        #hex digits
        resultBytes = self.__portConn.readline().decode()
        resultStr = ''.join(b for b in resultBytes if b in string.hexdigits)

        if(len(resultStr) < (2*len(data))):
            print('Length mismatch on read: {} {}'.format(len(resultStr),2*len(data)))
            return None
        else:
            bytes = bytearray.fromhex(resultStr)
            return list(bytes)


if __name__ == '__main__':
    print('Looking for a Linduino')
    l = linduinoSPI()
    if l.isConnected():
        print('Success!')
    else:
        print('Failed to find Linduino')

    del l