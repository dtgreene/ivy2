import bluetooth
import queue
import threading
import select

OUT_QUEUE_TIMEOUT = 0.1
IN_QUEUE_TIMEOUT = 0.1


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

        self.start()

    def connect(self):
        # create socket and connect
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self.mac, self.port))

        self.sock = sock
        self.alive.set()

    def run(self):
        while self.alive.is_set():
            # send any out bound messages
            try:
                # get the next out queue item
                message = self.outbound_q.get(True, OUT_QUEUE_TIMEOUT)

                self.sock.send(message)
            except queue.Empty:
                pass

            # check if the socket is readable
            result = select.select([self.sock], [], [], IN_QUEUE_TIMEOUT)

            # receive any incoming messages
            if result[0]:
                self.inbound_q.put(self.sock.recv(self.receive_size))

    def disconnect(self, timeout=None):
        if self.sock:
            self.sock.close()
            self.sock = None

        # unset the alive event so run() will not continue
        self.alive.clear()
        # block the calling thread until this thread completes
        threading.Thread.join(self, timeout)

    # def perform_task(self, task):
    #     message = task.get_packets()
    #     print("[Sent]: {}".format(message.hex()))

    #     # send the message
    #     self.sock.send(message)

    #     # receive a response while blocking
    #     response = self.sock.recv(4096)
    #     print("[Rcvd]: {}".format(response.hex()))

    #     payload, ack, error = serial.parse_in_packet(response)

    #     if error:
    #         print("Packet contained error: {}".format(error))

    #     task.on_read_data(response, payload, ack)
