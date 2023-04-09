def main():
    # data = bytes.fromhex("43f0000121000000014831ffff000000000000000000000000000000000000000000")
    # payload, ack, error = parse_in_packet(data)
    # print(payload, ack, error)
    end_index = 8000
    image_length = 12000
    progress = (end_index * 100) / image_length

    print("Progress: {}%".format(round(progress)))

def parse_in_packet(data):
    # get payload by skipping the first 8 bytes
    payload = data[8:len(data)]

    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return payload, ack, error

main()
