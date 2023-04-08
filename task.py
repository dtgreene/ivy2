import struct

import utils

START_CODE = 17167

COMMAND_START_SESSION = 0
COMMAND_GET_STATUS = 257
COMMAND_SETTING_ACCESSORY = 259
COMMAND_PRINT_READY = 769
COMMAND_REBOOT = 65535


class StatusTask:
    def get_packet(self):
        return bytes(get_base_packet(COMMAND_GET_STATUS))

    def on_read_data(self, data, payload, ack):
        i = (payload[0] << 8) | payload[1]

        error_code = payload[2]
        battery_level = utils.get_bit_range(i, 6)
        usb_status = (i >> 7) & 1

        status = error_code, battery_level, usb_status

        queue_flags = ((payload[4] & 255) << 8) | (payload[5] & 255)

        is_cover_open = queue_flags & 1 == 1
        is_no_paper = queue_flags & 2 == 2
        is_wrong_smart_sheet = queue_flags & 16 == 16

        flags = is_cover_open, is_no_paper, is_wrong_smart_sheet

        return status, flags


def get_base_packet(command, flag_1=False, flag_2=False):
    b1 = 1
    b2 = 32

    if flag_1:
        b1 = -1
        b2 = -1

    byte_array = bytearray(34)
    struct.pack_into(">HhbHB", byte_array, 0, START_CODE,
                     b1, b2, command, 1 if flag_2 else 0)

    return byte_array
