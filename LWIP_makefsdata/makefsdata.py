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
import argparse
import datetime
import glob
import os

####################################
# This script is a helper for generating the FS nodes for flash memory when
# working with the LWIP HTTP server.  The structure of the outputted C file is
# based on what the C and Perl applications provided by LWIP does, but ported
# to Python.
####################################

#Constants for HTTP content types. Add as necessary
HDR_HTML  = 'Content-type: text/html'
HDR_CSS   = 'Content-type: text/css'
HDR_GIF   = 'Content-type: image/gif'
HDR_PNG   = 'Content-type: image/png'
HDR_JPG   = 'Content-type: image/jpeg'
HDR_PLAIN = 'Content-type: text/plain'

#Dictionary matching file extensions to content types. Update as necessary
EXT_TO_HDR = { '.html': HDR_HTML,  '.htm': HDR_HTML, '.shtm': HDR_HTML,
               '.shtml': HDR_HTML, '.css': HDR_CSS,  '.gif': HDR_GIF,
               '.png': HDR_PNG,    '.jpg': HDR_JPG,  '.jpeg': HDR_JPG }

#List of extensions which imply SSI capabilities
SSI_EXTS = ['.shtm', '.shtml']


def BytesToC_Data(dataBytes: bytes, prefixIndStr: str = '', maxPerRow: int = 16):
    '''
    BytesToC_Data - Converts bytes into a C compatible string in the to be used
                    in an array declaration
        Inputs
        dataBytes - Bytes to convert
        prefixIndStr - Prefix string to append to the front of each line.
                       Would be spaces or tabs
        maxPerRow - Maximum number of bytes to put in line. For formatting

        Outputs
        String of C compatible bytes. Does not include braces or brackets
    '''
    outStr = ""
    for i in range(0, len(dataBytes), maxPerRow):
        outStr += (prefixIndStr +
                   ''.join('0x{:02x}, '.format(x) for x in dataBytes[i:i+maxPerRow]) +
                    '\n')
    return outStr


class FS_Data:
    '''
    Class for holding information on a data node.  Minimal function
    '''
    def __init__(self, path: str, header: str, content: bytes, isSsi: bool):
        '''
        __init__ Class constructor. Sets up the data elements

        Inputs
        path - File path and filename, relative to HTTP folder
        header - Fixed header for responses
        content - Bytes for the file data
        isSsi - Flag is SSI capable file
        '''
        #Fix in case working in Windows
        self.path = path.replace('\\','/')

        #Need a starting slash
        if not self.path.startswith('/'):
            self.path = '/' + self.path

        #For use in the C files, replace all path symbols with _'s
        self.prefix = path.replace('/', '_').replace('.','_').replace('\\', '_').replace('-','_')
        self.header = header
        self.content = content
        self.isSsi = isSsi


# Application entry point.
# Optional argument is the path location for all the web files. If not provided
# will assume ./fs
if __name__ == '__main__':
    #Define the command line arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", help="Input path location for the web files", default='./fs/')
    argParser.add_argument("-o", "--output", help="Output file name", default='fsdata.c')
    args = argParser.parse_args()
    path = args.input

    #Recursively grab all the files
    dataFiles = glob.glob(path + '/**/*.*', recursive=True)

    #Initialize the empty list
    fsData = []

    print('Parsing files from:', path)

    #Process the files
    for file in dataFiles:
        #Assume not SSI
        isSsi = False

        #Grab just the file name
        dname,fname = os.path.split(file)

        #There is a special case for 404.html.  A bit dumb here, as you could
        #have an image starting with 404. Should be ok in a custom embedded
        #system
        if(fname.startswith('404')):
            header = 'HTTP/1.0 404 File not found\n'
        else: #Normal HTTP OK
            header = 'HTTP/1.0 200 OK\n'

        #LWIP Server information
        header += 'Server: lwIP/2.2.0 (http://savannah.nongnu.org/projects/lwip)\n'

        #Grab the file extension
        ext = os.path.splitext(fname)[1]

        #Grab the data from the dictionary
        try:
            header += EXT_TO_HDR[ext] + '\n\n'
        except:
            #Otherwise assume just plain text
            header += HDR_PLAIN + '\n\n'

        #Check if an SSI file
        if ext in SSI_EXTS:
            isSsi  = True

        #Grab the actual file data as bytes
        with open(file, 'rb') as inF:
            content = inF.read()

        #Clean up for Window's slashes
        file = file.replace('\\', '/')

        #Notify the user of progess
        print('Processing', file.removeprefix(path))

        #Add a new instance to the list. Ditch the path from the start of file
        fsData.append( FS_Data(file.removeprefix(path), header, content, isSsi))

    #Notify the user of progress
    print('Generating output file', args.output)

    #Generate the actual C file.
    outputFile = open(args.output, 'w')
    outputFile.write('/**\n' +
                     ' * This file was autogenerated on ' + str(datetime.datetime.now()) + '.\n' +
                     ' * It is recommended to regenerate if changes are needed.\n' +
                     ' * Proceed with caution if manually editing\n */\n')
    outputFile.write(('#include "lwip/apps/fs.h"\n' +
                      '#include "lwip/def.h"\n\n' +
                      '#define file_NULL (struct fsdata_file *) NULL\n\n' +
                      '#ifndef FSDATA_ALIGN_PRE\n' +
                      '#define FSDATA_ALIGN_PRE\n' +
                      '#endif\n' +
                      '#ifndef FSDATA_ALIGN_POST\n' +
                      '#define FSDATA_ALIGN_POST\n' +
                      '#endif\n\n\n'))

    #Generate the code for the raw data
    for fsd in fsData:
        outputFile.write('#define {:s}_name "{:s}"\n'.format(fsd.prefix, fsd.path))
        outputFile.write('static const unsigned char FSDATA_ALIGN_PRE {:s}_data[] FSDATA_ALIGN_POST = {{\n'.format(fsd.prefix))
        outputFile.write('/*\n{:s}*/\n'.format(fsd.header))
        outputFile.write(BytesToC_Data(fsd.header.encode('utf-8'),'    ', 16))
        outputFile.write('\n/* Data */\n')
        outputFile.write(BytesToC_Data(fsd.content, '    ', 16))
        outputFile.write('};\n\n')

    #Just a file separator
    outputFile.write('/******************************************/\n\n')

    #Create the structs and linked list. Generated tail first, so next is NULL
    nextNode = 'file_NULL'
    for fsd in fsData:
        outputFile.write('const struct fsdata_file file_{:s}[] = {{{{\n'.format(fsd.prefix))
        outputFile.write('    {:s},\n'.format(nextNode))
        outputFile.write('    (unsigned char*){:s}_name,\n'.format(fsd.prefix))
        outputFile.write('    {:s}_data,\n'.format(fsd.prefix))
        outputFile.write('    {:d},\n'.format(len(fsd.header) + len(fsd.content)))
        if fsd.isSsi:
            outputFile.write('    FS_FILE_FLAGS_HEADER_INCLUDED | FS_FILE_FLAGS_HEADER_PERSISTENT | FS_FILE_FLAGS_SSI,\n')
        else:
            outputFile.write('    FS_FILE_FLAGS_HEADER_INCLUDED | FS_FILE_FLAGS_HEADER_PERSISTENT,\n')
        outputFile.write('}};\n\n')
        nextNode = 'file_' + fsd.prefix

    outputFile.write('#define FS_ROOT {:s}\n'.format(nextNode))
    outputFile.write('#define FS_NUMFILES {:d}\n'.format(len(fsData)))
    outputFile.close()
