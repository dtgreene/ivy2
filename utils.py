def get_bit_range(input, stop):
    str = ""

    for i in range(stop + 1):
        str += "1" if ((input >> i) & 1) == 1 else "0"

    try:
        return int(str[::-1], 2)
    except:
        return 0
