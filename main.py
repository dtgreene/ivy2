# sudo hciconfig 0 sspmode 0

import bluetooth
import time

import utils
import serial

PRINTER_MAC = "04:7F:0E:B7:46:0B"
PRINTER_SERIAL_PORT = 1
PRINTER_MAX_TRANSFER_UNIT = 65535

task_listeners = {
  serial.ACK_GET_STATUS: [],
  serial.ACK_START_SESSION: [],
  serial.ACK_GET_STATUS: [],
  serial.ACK_SETTING_ACCESSORY: [],
  serial.ACK_PRINT_READY: [],
  serial.ACK_REBOOT: [],
}

def main():
  print("Connecting to {} on port {}".format(PRINTER_MAC, PRINTER_SERIAL_PORT))

  # Create the client socket
  sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
  sock.connect((PRINTER_MAC, PRINTER_SERIAL_PORT))

  print("Connected")

  time.sleep(1)
  sock.send(serial.start_session())

  try:
    while True:
      data = sock.recv(4096)

      if not data:
        break

      handle_response(data)

  except OSError:
    pass

  print("Disconnected.")
  sock.close()

def handle_response(data): 
  payload, ack, error = serial.parse_in_packet(data)

  print("Received response: ack: {}, error: {}".format(ack, error))

  # parse response
  if ack == serial.ACK_START_SESSION:
    battery_level = utils.get_bit_range(((data[9] << 8) | (data[10])), 6)
    mtu = (((data[11] & 255) << 8) | (data[12] & 255))

    print("Start session: mtu: {}, battery level: {}".format(mtu, battery_level))
  elif ack == serial.ACK_GET_STATUS:
    i = (payload[0] << 8) | payload[1]

    error_code = payload[2]
    battery_level = utils.get_bit_range(i, 6)
    usb_status = (i >> 7) & 1

    queue_flags = ((payload[4] & 255) << 8) | (payload[5] & 255)

    is_cover_open = queue_flags & 1 == 1
    is_no_paper = queue_flags & 2 == 2
    is_wrong_smart_sheet = queue_flags & 16 == 16

    print("Status: error code: {}, battery level: {}, usb status: {}, cover open: {}, no paper: {}, wrong smart sheet: {}".format(
      error_code, 
      battery_level, 
      usb_status, 
      is_cover_open, 
      is_no_paper, 
      is_wrong_smart_sheet
    ))
  elif ack == serial.ACK_PRINT_READY:
    unknown = payload[2] & 255
    error_code = payload[3] & 255

    print("Print ready: unknown: {}, error code: {}".format(unknown, error_code))

main()