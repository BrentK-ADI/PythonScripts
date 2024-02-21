# LWIP Makefsdata
This script provides a Python implementation of a C code generator to create
LWIP HTTPD compliant FS files for embedded webpages in a Microcontroller
environment.

The code intends to be compliant with the output of the C or Perl makefsdata
provided by the [lwip project](https://github.com/lwip-tcpip/lwip)

## Usage
By default, the script assumes the source web data is located in the ./fs
subfolder of the executing location, and the output file will be fsdata.c.

Optionally, the input location and output file may be specified from the
command line
```
usage: makefsdata.py [-h] [-i INPUT] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input path location for the web files
  -o OUTPUT, --output OUTPUT
                        Output file name
```
