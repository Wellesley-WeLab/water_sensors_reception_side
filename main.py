#! /usr/bin/env python3

"""
This component should read the messages sent from the receiving device to the serial port.
After receiving the message the data will be stored in the database. The Web App will
get that data and show it.
"""

import serial
import sys
import argparse
import config

from models import *

PACKET_LEN = 29

# create command line arguments parser
parser = argparse.ArgumentParser(
    description='To read data from the receiving device, using serial communication.')
# option to indicate the serial port
parser.add_argument(
    '--port', help='The serial port that the device is connected to (ex: /dev/ttyUSB0)')
# option to indicate the baud rate
parser.add_argument('--baud_rate', help='The baud rate of the serial connection (ex: 9600)')


def hexRepr (string) :
    """
    Returns the hexadecimal representation of a byte string
    """

    return "0x" + "".join("{:02x}".format(b) for b in string)


def bytesToNumber (bts) :
    """
    Converts a list of bytes to the integer they represent.
    The first bytes in the array should be the most significant
    """

    value = 0
    lenBts = len(bts)
    for i in range (0, lenBts) :
        value += bts[i] << ((lenBts-i-1)*8)
    return value


def getPacketComponents (packet) :
    """
    Split the packet into it's components, according to the format:\n
    | packet no. (4 bytes) | reservoir id (1 byte) | water gap (4 bytes) | vcc (4 bytes) | tds (4 bytes) |
    | conductivity (4 bytes) | salinity (4 bytes) |  pH (4 bytes) |
    """

    try :
        result = {
            'packetNr': bytesToNumber(packet[0:4]),
            'reservoir': bytesToNumber(packet[4:5]),
            'waterGap': bytesToNumber(packet[5:9]),
            'vcc': bytesToNumber(packet[9:13]),
            'conductivity': bytesToNumber(packet[13:17]),
            'salinity': bytesToNumber(packet[17:21]),
            'tds': bytesToNumber(packet[21:25]),
            'pH': bytesToNumber(packet[25:29]),
        }
    except Exception as e:
        print("[main#getPacketComponents] packet with invalid format received: {}".format(e))
        return None

    return result


if __name__ == '__main__' :
    cmdArgs = parser.parse_args()
    # port and baud rate are required
    if cmdArgs.port == None or cmdArgs.baud_rate == None :
        print('both the serial port and the baud rate arguments are required.')
        parser.print_usage()
        sys.exit(1)

    print('App started...')

    serialCon = serial.Serial(port=cmdArgs.port, baudrate=cmdArgs.baud_rate)
    print('Connected to {}'.format(serialCon))

    # read the serial port continuously
    while True :
        packet = serialCon.read(PACKET_LEN)
        print('[main] DEBUG: Read {}'.format(hexRepr(packet)))
        # split the packet into its parts
        resultData = getPacketComponents(packet)
        if resultData is None :
            print('[main] unable to save this measuremet. Corrupted data')
        else :
            measurement = Measurement(**resultData)
            print('{}'.format(measurement))
            measurement.save()
