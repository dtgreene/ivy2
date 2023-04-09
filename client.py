import bluetooth
import queue
import threading
import select
import socket

QUEUE_TIMEOUT_OUT = 0.1
QUEUE_TIMEOUT_IN = 0.1

# the amount of time without sending any messages before disconnecting
AUTO_DISCONNECT_TIMEOUT = 30

class ClientThread(threading.Thread):
    def __init__(self, mac, port, receive_size=4096):
        super().__init__()

        self.mac = mac
        self.port = port
        self.receive_size = receive_size

        self.sock = None
        self.alive = threading.Event()

        self.outbound_q = queue.Queue()
        self.inbound_q = queue.Queue()

        self.disconnect_timer = threading.Timer(AUTO_DISCONNECT_TIMEOUT, self.disconnect)

        self.start()

    def connect(self):
        # create socket and connect
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self.mac, self.port))

        self.sock = sock
        self.alive.set()

    def run(self):
        while self.alive.is_set():
            # check that the socket is still active
            try:
                self.sock.getpeername()
            except socket.error:
                self.disconnect()

            # send any out bound messages
            try:
                # get the next out queue item
                message = self.outbound_q.get(True, QUEUE_TIMEOUT_OUT)

                self.sock.send(message)

                # reset the timer
                self.disconnect_timer.cancel()
                self.disconnect_timer = threading.Timer(AUTO_DISCONNECT_TIMEOUT, self.disconnect)
            except queue.Empty:
                pass

            # check if the socket is readable
            result = select.select([self.sock], [], [], QUEUE_TIMEOUT_IN)

            # receive any incoming messages
            if result[0]:
                self.inbound_q.put(self.sock.recv(self.receive_size))

    def disconnect(self, timeout=None):
        if self.sock:
            self.sock.close()
            self.sock = None

        self.disconnect_timer.cancel()

        # unset the alive event so run() will not continue
        self.alive.clear()
        # block the calling thread until this thread completes
        threading.Thread.join(self, timeout)
