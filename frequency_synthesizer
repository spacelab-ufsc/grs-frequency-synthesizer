import zmq
import time

class FrequencySynthesizer:
    def __init__(self, iq_receiver_socket_address, station_manager_pub_address):
        self.center_freq = None
        self.doppler_offset = 0

        self.context = zmq.Context()

        self.cmd_socket = self.context.socket(zmq.PUB)
        self.cmd_socket.bind(iq_receiver_socket_address)

        self.manager_socket = self.context.socket(zmq.SUB)
        self.manager_socket.connect(station_manager_pub_address)
        self.manager_socket.setsockopt_string(zmq.SUBSCRIBE, "freq")
        self.manager_socket.setsockopt_string(zmq.SUBSCRIBE, "doppler")

        self._running = False

    def _effective_frequency(self):
        return self.center_freq + self.doppler_offset

    def _send_tune(self):
        if self.center_freq is None:
            return
        freq = self._effective_frequency()
        self.cmd_socket.send_multipart([b"tune", str(freq).encode()])

    def run(self):
        print("[Synthesizer] Running")
        self._running = True

        try:
            while self._running:
                try:
                    topic, data = self.manager_socket.recv_multipart(flags=zmq.NOBLOCK)
                    topic = topic.decode()
                    value = int(float(data.decode()))

                    if topic == "freq":
                        self.center_freq = value
                        self.doppler_offset = 0
                        self._send_tune()

                    elif topic == "doppler":
                        if self.center_freq is None:
                            print("Set center frequency before doppler shift")
                        else:
                            self.doppler_offset = value
                            self._send_tune()

                except zmq.Again:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._running = False
        self.cmd_socket.close()
        self.manager_socket.close()
        self.context.term()
