import bluetooth
import queue
import threading
from loguru import logger

# the amount of time without sending any messages before disconnecting
AUTO_DISCONNECT_TIMEOUT = 30

OUTBOUND_QUEUE_TIMEOUT = 0.1


class ClientThread(threading.Thread):
    def __init__(self, receive_size=4096):
        super().__init__()

        self.receive_size = receive_size

        self.sock = None
        self.alive = threading.Event()

        self.outbound_q = queue.Queue()
        self.inbound_q = queue.Queue()

        self.disconnect_timer = threading.Timer(
            AUTO_DISCONNECT_TIMEOUT, self.disconnect)

    def connect(self, mac, port):
        # create socket and connect
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((mac, port))

        self.sock = sock
        self.alive.set()
        self.start()

    def run(self):
        while self.alive.is_set():
            # check that the socket is still active
            try:
                self.sock.getpeername()
            except bluetooth.btcommon.BluetoothError:
                self.disconnect()

            # block for sending messages
            self.sock.setblocking(True)

            # send any out bound messages
            try:
                # get the next out queue item
                message = self.outbound_q.get(True, OUTBOUND_QUEUE_TIMEOUT)

                logger.info(
                    "Sending message; approx. queue size: {}",
                    self.outbound_q.qsize()
                )
                self.sock.send(message)

                # reset the timer
                self.disconnect_timer.cancel()
                self.disconnect_timer = threading.Timer(
                    AUTO_DISCONNECT_TIMEOUT,
                    self.disconnect
                )
            except queue.Empty:
                pass

            # skip blocking for receiving messages, an exception will be raised if there's no data
            self.sock.setblocking(False)

            # receive incoming messages
            try:
                self.inbound_q.put(self.sock.recv(self.receive_size))
            except bluetooth.btcommon.BluetoothError:
                pass

    def disconnect(self, timeout=None):
        if self.sock:
            self.sock.close()

        self.disconnect_timer.cancel()

        # unset the alive event so run() will not continue
        self.alive.clear()

        try:
            # block the calling thread until this thread completes
            threading.Thread.join(self, timeout)
        except RuntimeError:
            pass
