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