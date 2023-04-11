import time
import queue
from loguru import logger

from task import (
    StartSessionTask,
    GetStatusTask,
    GetSettingTask,
    SetSettingTask,
    GetPrintReadyTask,
    RebootTask
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
from utils import parse_incoming_message

PRINT_BATTERY_MIN = 30
PRINT_DATA_CHUNK = 990


class Ivy2Printer:
    client = ClientThread()

    def connect(self, mac_address, port=1):
        self.client.connect(mac_address, port)
        self.__start_session()

        logger.debug("Connected")

    def disconnect(self):
        self.client.disconnect()
    
    def is_connected(self):
        return self.client.alive.is_set()

    def print(self, target, transfer_timeout=60):
        image_data = bytes()

        if type(target) is str:
            image_data = image.prepare_image(target)
        elif type(target) is bytes:
            image_data = target
        else:
            raise ValueError(
                "Unsupported target; expected string or bytes but got {}".format(
                    type(target)
                )
            )

        image_length = len(image_data)

        self.check_print_worthiness()
        self.get_setting()

        # setup the printer to receive the image data
        self.get_print_ready(image_length)

        # split up the image and add to the client queue
        start_index = 0
        while True:
            end_index = min(start_index + PRINT_DATA_CHUNK, image_length)
            image_chunk = image_data[start_index:end_index]

            self.client.outbound_q.put(image_chunk)

            if end_index >= image_length:
                break

            start_index = end_index

        logger.debug("Beginning data transfer...")

        # wait longer than usual since the transfer takes some time
        self.__receive_message(transfer_timeout)

        logger.debug("Data transfer complete! Printing should begin in a moment")

    def reboot(self):
        return self.__perform_task(RebootTask())

    def get_status(self):
        return self.__perform_task(GetStatusTask())

    def get_setting(self):
        return self.__perform_task(GetSettingTask())

    def set_setting(self, color_id, auto_power_off):
        return self.__perform_task(SetSettingTask(color_id, auto_power_off))

    def get_print_ready(self, length):
        return self.__perform_task(GetPrintReadyTask(length))

    def check_print_worthiness(self):
        status = self.get_status()
        error_code, battery_level, _, is_cover_open, is_no_paper, is_wrong_smart_sheet = status

        if error_code != 0:
            logger.error(
                "Status contains a non-zero error code: {}",
                error_code
            )

        if battery_level < PRINT_BATTERY_MIN:
            raise LowBatteryError()

        if is_cover_open:
            raise CoverOpenError()

        if is_no_paper:
            raise NoPaperError()

        if is_wrong_smart_sheet:
            raise WrongSmartSheetError()

    def __start_session(self):
        return self.__perform_task(StartSessionTask())

    def __perform_task(self, task):
        # send the task's message
        self.__send_message(task.get_message())
        response = self.__receive_message()

        if response[2] != task.ack:
            raise AckError("Got invalid ack; expected {} but got {}".format(
                task.ack, response[3]
            ))

        # process and return the response
        return task.process_response(response)

    def __send_message(self, message):
        if not self.client.alive.is_set():
            raise ClientUnavailableError()

        # add the message to the client thread's outbound queue
        self.client.outbound_q.put(message)

    def __receive_message(self, timeout=5):
        start = int(time.time())
        while int(time.time()) < (start + timeout):
            if not self.client.alive.is_set():
                raise ClientUnavailableError("")

            try:
                # attempt to read the client thread's inbound queue
                response = parse_incoming_message(
                    self.client.inbound_q.get(False, 0.1)
                )

                logger.debug(
                    "Received message: ack: {}, error: {}",
                    response[2],
                    response[3]
                )
                return response
            except queue.Empty:
                pass

        raise ReceiveTimeoutError()
