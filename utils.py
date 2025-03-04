def parse_bit_range(input, size):
    str = ""

    for i in range(size):
        str += "1" if ((input >> i) & 1) == 1 else "0"

    try:
        return int(str[::-1], 2)
    except:
        return 0


def parse_incoming_message(data):
    """General parser for all messages coming from the printer."""

    payload = data[8:len(data)]
    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return data, payload, ack, error
