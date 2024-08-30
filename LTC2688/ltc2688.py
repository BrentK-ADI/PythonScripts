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

class ltc2688:
    '''
    ltc2688 - Basic class for interfacing with the LTC2688/2686 parts. The
              class assumes the linduinoSPI or similar controller being used
    '''
    #Device constants. Register commands and bit values
    CMD_WRITE_DAC_CODE_MASK        = 0x00
    CMD_WRITE_CH_SETTINGS_MASK     = 0x10
    CMD_WRITE_OFFSET_ADJ_MASK      = 0x20
    CMD_WRITE_GAIN_ADJ_MASK        = 0x30
    CMD_WRITE_CODE_UPDATE_MASK     = 0x40
    CMD_WRITE_CODE_UPDATE_ALL_MASK = 0x50
    CMD_UPDATE_CHANNEL_MASK        = 0x60
    CMD_WRITE_CONFIG               = 0x70
    CMD_WRITE_POWER_DOWN           = 0x71
    CMD_WRITE_AB_SELECT            = 0x72
    CMD_WRITE_SW_TOGGLE            = 0x73
    CMD_WRITE_DITHER               = 0x74
    CMD_WRITE_MUX_CTRL             = 0x75
    CMD_WRITE_FAULT                = 0x76
    CMD_WRITE_CODE_ALL             = 0x78
    CMD_WRITE_CODE_ALL_UPDATE      = 0x79
    CMD_WRITE_SETTINGS_ALL         = 0x7A
    CMD_WRITE_SETTINGS_UPDATE_ALL  = 0x7B
    CMD_UPDATE_ALL                 = 0x7C

    #Values for the Span field of the settings register
    SPAN_0_5V    = 0x00
    SPAN_0_10V   = 0x01
    SPAN_N5_5V   = 0x02
    SPAN_N10_10V = 0x03
    SPAN_N15_15V = 0x04
    SPAN_5PERCENT_OVER_BIT = 0x08 #Bit to include 5# over range

    #Specify the bit depth of this chip
    DEPTH_12_BIT = 0
    DEPTH_16_BIT = 1

    #Specify the device type
    DEVICE_LTC2686 = 0
    DEVICE_LTC2688 = 1


    #Initializes the class
    def __init__(self, controller, deviceType, depth):
        self.__controller = controller

        if (depth != self.DEPTH_12_BIT) and (depth != self.DEPTH_16_BIT):
            raise Exception('Invalid depth provided')
        self.__depth = depth

        if (deviceType != self.DEVICE_LTC2686) and (deviceType != self.DEVICE_LTC2688):
            raise Exception('Invalid device type provided')
        self.__device = deviceType


    #Sets the span for a channel
    def setSpan(self, ch, span):
        '''
        setSpan - Method to set the span value for the provided channel

            Inputs
            ch - Channel to set. 0 based
            span - Span to set. use the SPAN_ constants
        '''
        if(self.__device == self.DEVICE_LTC2688) and (ch > 15):
           raise Exception('Invalid channel number for LTC2688')

        if(self.__device == self.DEVICE_LTC2686) and (ch > 7):
           raise Exception('Invalid channel number for LTC2686')

        #For the LTC2686, the address is shift left by 1
        if(self.__device == self.DEVICE_LTC2686):
            ch = ch << 1

        self.writeReg(self.CMD_WRITE_CH_SETTINGS_MASK | ch, span)


    #Sets the output value for a channel
    def setChannelCode(self, ch, code):
        '''
        setChannelCode - Method to set the span value for the provided channel
                            NOTE: Update needs to be called on all or the channel
                            for the value to take affect.

            Inputs
            ch - Channel to set. 0 based
            span - Span to set. use the SPAN_ constants
        '''
        if(self.__device == self.DEVICE_LTC2688) and (ch > 15):
           raise Exception('Invalid channel number for LTC2688')

        if(self.__device == self.DEVICE_LTC2686) and (ch > 7):
           raise Exception('Invalid channel number for LTC2686')

        #For the LTC2686, the address is shift left by 1
        if(self.__device == self.DEVICE_LTC2686):
            ch = ch << 1

        #12-bit data is left justified, so shift left by 4
        if( self.__depth == self.DEPTH_12_BIT ):
            code = code << 4

        self.writeReg(self.CMD_WRITE_DAC_CODE_MASK | ch, code)


    #Performs an update of all DAC codes
    def updateAll(self):
        '''
            updateAll - Sends an update request to all channels to update the DAC
                        output to the latest register value
        '''
        self.writeReg(self.CMD_UPDATE_ALL, 0x00)


    #Performs a generic register write
    def writeReg(self, reg, value):
        '''
            writeReg - Generic method for writing a chip register

            Inputs
            reg - Register to write
            value - Value to write, 16-bits
        '''
        #Get the individual bytes from the value
        regVal = [(value & (0xFF << pos)) >> pos for pos in range(0,9,8)]

        #Build the SPI frame and send
        data = [reg, regVal[1], regVal[0]];
        self.__controller.writeRead(data);

