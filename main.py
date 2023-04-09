import time
import bluetooth
import queue
from loguru import logger

from task import (
    StartSessionTask,
    GetStatusTask,
    GetSettingTask,
    GetPrintReadyTask
)
import image

from exceptions import (
    ClientUnavailableError,
    ReceiveTimeoutError,
    AckError,
    LowBatteryError,
    CoverOpenError,
    NoPaperError,
    WrongSmartSheetError
)
from client import ClientThread

PRINTER_MAC = "04:7F:0E:B7:46:0B"
PRINTER_SERIAL_PORT = 1

PRINT_BATTERY_MIN = 30
PRINT_DATA_CHUNK = 990

client = ClientThread(PRINTER_MAC, PRINTER_SERIAL_PORT)


def main():
    logger.info("Connecting...")

    try:
        client.connect()
        logger.info("Connected")

        perform_task(StartSessionTask())

        # verify the printer is ready for printing
        printer_status = perform_task(GetStatusTask())
        check_print_worthiness(printer_status)

        # probably not necessary but mimicking the original
        perform_task(GetSettingTask())

        # prepare the image
        image_bytes = image.prepare_image("./assets/shrek.jpg")
        image_length = len(image_bytes)

        # let the printer know we about to start blasting data
        perform_task(GetPrintReadyTask(image_length))

        logger.info("Beginning data transfer...")

        start_index = 0
        while True:
            end_index = min(start_index + PRINT_DATA_CHUNK, image_length)
            image_chunk = image_bytes[start_index:end_index]

            client.outbound_q.put(image_chunk)

            progress = (end_index * 100) / image_length
            logger.info("Transfer progress: {}%", round(progress))

            if end_index >= image_length:
                break

            start_index = end_index
        
        logger.info("Data transfer complete!")

    except bluetooth.btcommon.BluetoothError as e:
        logger.error("Could not connect to printer: {}", e)

    client.disconnect()


def check_print_worthiness(status):
    error_code, battery_level, _, is_cover_open, is_no_paper, is_wrong_smart_sheet = status

    if error_code != 0:
        logger.error("Status contains a non-zero error code: {}", error_code)

    if battery_level < PRINT_BATTERY_MIN:
        raise LowBatteryError()

    if is_cover_open:
        raise CoverOpenError()

    if is_no_paper:
        raise NoPaperError()

    if is_wrong_smart_sheet:
        raise WrongSmartSheetError()


def perform_task(task):
    # send the task's message
    send_message(task.get_message())
    response = receive_message()

    if response[3] != task.ack:
        raise AckError("StartSessionTask got invalid ack; expected {} but got {}".format(
            task.ack, response[3]
        ))

    # process and return the response
    return task.process_response(receive_message())


def send_message(message):
    if not client.alive.is_set():
        raise ClientUnavailableError()

    logger.debug("Sending message: {}", message)
    # add the message to the client thread's outbound queue
    client.outbound_q.put(message)


def receive_message(timeout=5):
    start = int(time.time())
    while int(time.time()) < (start + timeout):
        if not client.alive.is_set():
            raise ClientUnavailableError()

        try:
            # attempt to read the client thread's inbound queue
            response = parse_incoming_message(client.inbound_q.get(False))
            logger.debug(
                "Received message: ack: {}, error: {}",
                response[2],
                response[3]
            )
            return response
        except queue.Empty:
            time.sleep(0.1)

    raise ReceiveTimeoutError()


def parse_incoming_message(data):
    """General parser for all messages coming from the printer."""

    payload = data[8:len(data)]
    ack = (data[6] & 255) | ((data[5] & 255) << 8)
    error = data[7] & 255

    return data, payload, ack, error


main()
