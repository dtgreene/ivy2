import time
import bluetooth

from exceptions import CommandTimedOutException, PrinterConnectException
from client import ClientThread

PRINTER_MAC = "04:7F:0E:B7:46:0B"
PRINTER_SERIAL_PORT = 1

def main():
    client = ClientThread(PRINTER_MAC, PRINTER_SERIAL_PORT)
    print("Connecting...")

    try:
        client.connect()
        print("Connected")
    except bluetooth.btcommon.BluetoothError as e:
        print("Could not connect to printer: {}".format(e))

    if client.alive.is_set():
        pass
    
    time.sleep(3)
    client.disconnect()

def retry(condition, timeout):
    start = int(time.time())
    while int(time.time()) < (start + timeout):
        if condition():
            return
        else:
            time.sleep(0.1)

    raise (CommandTimedOutException())

main()