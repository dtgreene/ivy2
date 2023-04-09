def main():
    data = bytes.fromhex("430f0001200101000000000000000000000000000000000000000000000000000000")
    payload, ack, error = parse_in_packet(data)
    print(payload, ack, error)

def parse_in_packet(data):
    # get payload by skipping the first 8 bytes
    payload = data[8:len(data)]

    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return payload, ack, error

main()
