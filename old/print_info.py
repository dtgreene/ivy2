import struct

import utils

ASCII_DLE = 16
BYTE_CONVERT_16 = 16711680


class PrinterInfo:
    def __init__(self, i, serialNumber, name, i2, i3, i4, i5, i6, i7, macAddress, i8, i9, s, i10, i11, i12, i13, i14, i15, z, i16, i17, z2, i18, z3):
        self.productCode = i
        self.serialNumber = serialNumber
        self.name = name
        self.errorCode = i2
        self.numberOfPhotoPrinted = i3
        self.printMode = i4
        self.batteryLevel = i5
        self.autoExposure = i6
        self.autoPowerOff = i7
        self.macAddress = macAddress
        self.firmwareVersion = i8
        self.tmdVersion = i9
        self.maxPayloadSize = s
        self.usbStatus = i10
        self.dualImageStatus = i11
        self.tmdReplaceStatus = i12
        self.aspectRatio = i13
        self.flashMode = i14
        self.timer = i15
        self.connecting = z
        self.printerQueueStatus = i16
        self.printerQueueFlags = i17
        self.connectProcessing = z2
        self.colorID = i18
        self.isOnline = z3

    def print(self):
        attrs = vars(self)
        print(', '.join("%s: %s" % item for item in attrs.items()))


def get_info_instance(i, str, str2, i2, i3, i4, i5, i6, i7, str3, i8, i9, s, i10, i11, i12, i13, i14, i15, z, i16, i17, z2, i18, z3, i19):
    return PrinterInfo(
        -1 if (i19 & 1) != 0 else i,
        "" if (i19 & 2) != 0 else str,
        "" if (i19 & 4) != 0 else str2,
        0 if (i19 & 8) != 0 else i2,
        0 if (i19 & 16) != 0 else i3,
        0 if (i19 & 32) != 0 else i4,
        0 if (i19 & 64) != 0 else i5,
        0 if (i19 & 128) != 0 else i6,
        0 if (i19 & 256) != 0 else i7,
        str3 if (i19 & 512) == 0 else "",
        0 if (i19 & 1024) != 0 else i8,
        0 if (i19 & 2048) != 0 else i9,
        # (short)
        0 if (i19 & 4096) != 0 else s,
        0 if (i19 & 8192) != 0 else i10,
        0 if (i19 & 16384) != 0 else i11,
        0 if (i19 & 32768) != 0 else i12,
        0 if (i19 & 65536) != 0 else i13,
        0 if (i19 & 131072) != 0 else i14,
        0 if (i19 & 262144) != 0 else i15,
        False if (i19 & 524288) != 0 else z,
        0 if (i19 & 1048576) != 0 else i16,
        0 if (i19 & 2097152) != 0 else i17,
        False if (i19 & 4194304) != 0 else z2,
        0 if (i19 & 8388608) != 0 else i18,
        False if (i19 & 16777216) != 0 else z3
    )


def parse_setting_data(input):
    version_bytes = bytearray(input[1:4])
    version_number = (version_bytes[2] & 255) | (
        (version_bytes[0] << ASCII_DLE) & BYTE_CONVERT_16) | ((version_bytes[1] << 8) & 65280)
    additional_bytes = struct.unpack('>hbb', input[5:9])

    return get_info_instance(
        0,
        None,
        None,
        0,
        additional_bytes[0],
        0,
        0,
        0,
        input[0],
        None,
        version_number,
        additional_bytes[1],
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        False,
        0,
        0,
        False,
        additional_bytes[2],
        False,
        25162479
    )


def parse_status_data(input):
    i = (input[0] << 8) | input[1]
    return get_info_instance(
        0,
        None,
        None,
        input[2],
        0,
        0,
        utils.get_bit_range(i, 6),
        0,
        0,
        None,
        0,
        0,
        0,
        (i >> 7) & 1,
        0,
        0,
        0,
        0,
        0,
        False,
        input[3] & 255,
        ((input[4] & 255) << 8) | (input[5] & 255),
        False,
        0,
        False,
        30400439
    )
