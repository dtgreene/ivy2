import struct

START_CODE = 17167

COMMAND_START_SESSION = 0
COMMAND_GET_STATUS = 257
COMMAND_SETTING_ACCESSORY = 259
COMMAND_PRINT_READY = 769
COMMAND_REBOOT = 65535

ACK_START_SESSION = 0
ACK_GET_STATUS = 257
ACK_SETTING_ACCESSORY = 259
ACK_PRINT_READY = 769
ACK_REBOOT = 65535

# https://docs.python.org/3.7/library/struct.html


def setting_accessory():
    return bytes(__get_out_packet(COMMAND_SETTING_ACCESSORY))


def start_session():
    return bytes(__get_out_packet(COMMAND_START_SESSION, True, False))


def status():
    return bytes(__get_out_packet(COMMAND_GET_STATUS))


def print_ready(length, flag):
    packet_bytes = __get_out_packet(COMMAND_PRINT_READY)

    b0 = (((-16777216) & length) >> 24)
    b1 = ((16711680 & length) >> 16)
    b2 = ((65280 & length) >> 8)
    b3 = (length & 255)
    b4 = 1
    b5 = 2 if flag else 1

    struct.pack_into('>BBBBBB', packet_bytes, 8, b0, b1, b2, b3, b4, b5)

    return bytes(packet_bytes)


def reboot():
    packet_bytes = __get_out_packet(COMMAND_REBOOT, False, True)

    struct.pack_into('>B', packet_bytes, 8, 1)

    return bytes(packet_bytes).hex()


def __get_out_packet(command, flag_1=False, flag_2=False):
    b1 = 1
    b2 = 32

    if flag_1:
        b1 = -1
        b2 = -1

    byte_array = bytearray(34)
    struct.pack_into(">HhbHB", byte_array, 0, START_CODE,
                     b1, b2, command, 1 if flag_2 else 0)

    return byte_array


def parse_in_packet(data):
    # get payload by skipping the first 8 bytes
    payload = data[8:len(data)]

    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return payload, ack, error
