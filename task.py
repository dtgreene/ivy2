import struct

from utils import parse_battery_level

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

AUTO_OFF_NEVER = 0
AUTO_OFF_THREE = 3
AUTO_OFF_FIVE = 5
AUTO_OFF_TEN = 10

COLOR_DEFAULT = 0
COLOR_GREEN = 1
COLOR_BLUE = 2

class BaseTask:
    def process_response(self, _):
        pass


class StartSessionTask(BaseTask):
    ack = ACK_START_SESSION

    def get_message(self):
        return bytes(get_base_message(COMMAND_START_SESSION, True, False))

    def process_response(self, response):
        data = response[0]

        battery_level = parse_battery_level((data[9] << 8) | (data[10]))
        mtu = (((data[11] & 255) << 8) | (data[12] & 255))

        return battery_level, mtu


class GetSettingTask(BaseTask):
    ack = ACK_SETTING_ACCESSORY

    def get_message(self):
        return bytes(get_base_message(COMMAND_SETTING_ACCESSORY))

    def process_response(self, response):
        payload = response[1]
        
        auto_power_off = struct.unpack('B', payload[:1])[0]

        return auto_power_off


class SetSettingTask(BaseTask):
    ack = ACK_SETTING_ACCESSORY

    def __init__(self, color_id, auto_power_off):
        super().__init__()

        self.color_id = color_id
        self.auto_power_off = auto_power_off

    def get_message(self):
        base_message = get_base_message(COMMAND_SETTING_ACCESSORY, False, True)

        struct.pack_into(
            '>BB',
            base_message,
            8,
            self.color_id,
            self.auto_power_off
        )

        return bytes(base_message)


class RebootTask(BaseTask):
    ack = ACK_REBOOT

    def get_message(self):
        base_message = get_base_message(COMMAND_REBOOT, False, True)

        struct.pack_into('>B', base_message, 8, 1)

        return bytes(base_message)


class GetStatusTask(BaseTask):
    ack = ACK_GET_STATUS

    def get_message(self):
        return bytes(get_base_message(COMMAND_GET_STATUS))

    def process_response(self, response):
        payload = response[1]

        i = (payload[0] << 8) | payload[1]

        error_code = payload[2]
        battery_level = parse_battery_level(i)
        usb_status = (i >> 7) & 1

        queue_flags = ((payload[4] & 255) << 8) | (payload[5] & 255)

        is_cover_open = queue_flags & 1 == 1
        is_no_paper = queue_flags & 2 == 2
        is_wrong_smart_sheet = queue_flags & 16 == 16

        return error_code, battery_level, usb_status, is_cover_open, is_no_paper, is_wrong_smart_sheet


class GetPrintReadyTask(BaseTask):
    ack = ACK_PRINT_READY

    def __init__(self, length, flag = False):
        super().__init__()

        self.length = length
        self.flag = flag

    def get_message(self):
        base_message = get_base_message(COMMAND_PRINT_READY)

        b0 = (((-16777216) & self.length) >> 24)
        b1 = ((16711680 & self.length) >> 16)
        b2 = ((65280 & self.length) >> 8)
        b3 = (self.length & 255)
        b4 = 1
        b5 = 2 if self.flag else 1

        struct.pack_into('>BBBBBB', base_message, 8, b0, b1, b2, b3, b4, b5)

        return bytes(base_message)

    def process_response(self, response):
        payload = response[1]

        unknown = payload[2] & 255
        error_code = payload[3] & 255

        return unknown, error_code


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
        START_CODE,
        b1,
        b2,
        command,
        1 if flag_2 else 0
    )

    return byte_array
