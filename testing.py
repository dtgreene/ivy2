import time
import struct
from socket import socket, AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM

import utils

PRINTER_MAC = "04:7F:0E:B7:46:0B"
PRINTER_SERIAL_PORT = 1

PRINTER_START_CODE = 17167

COMMAND_START_SESSION = 0
COMMAND_GET_STATUS = 257

def main():
    data = bytes.fromhex("43f000012101010044ac000000000000000000000000000000000000000000000000")
    response = parse_in_packet(data)
    print(response[0].hex())
    
    if response[1] == COMMAND_GET_STATUS:
        print(process_status_response(response))

    # sock = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)
    # sock.connect((PRINTER_MAC, PRINTER_SERIAL_PORT))

    # time.sleep(2)
    # sock.send(bytes(get_base_message(COMMAND_GET_STATUS, True, False)))
    # time.sleep(2)
    # data = sock.recv(1024)

    # print(data.hex())

def process_status_response(response):
    payload = response[0]

    i = (payload[0] << 8) | payload[1]

    error_code = payload[2]
    battery_level = utils.get_bit_range(i, 6)
    usb_status = (i >> 7) & 1

    queue_flags = ((payload[4] & 255) << 8) | (payload[5] & 255)

    is_cover_open = queue_flags & 1 == 1
    is_no_paper = queue_flags & 2 == 2
    is_wrong_smart_sheet = queue_flags & 16 == 16

    return error_code, battery_level, usb_status, is_cover_open, is_no_paper, is_wrong_smart_sheet


def parse_in_packet(data):
    # get payload by skipping the first 8 bytes
    payload = data[8:len(data)]

    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return payload, ack, error

def get_base_message(command, flag_1=False, flag_2=False):
    b1 = 1
    b2 = 32

    if flag_1:
        b1 = -1
        b2 = -1

    byte_array = bytearray(34)
    struct.pack_into(
        ">HhbHB",
        byte_array,
        0,
        PRINTER_START_CODE,
        b1,
        b2,
        command,
        1 if flag_2 else 0
    )

    return byte_array

main()
