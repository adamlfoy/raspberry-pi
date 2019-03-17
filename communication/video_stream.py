from communication.server import Server
from dill import dumps
from socket import timeout
from threading import Thread


class VideoStream(Server):

    def __init__(self, ip="localhost", port=50001):

        # Super TCP data exchange functionality
        super()._init_high_level(ip=ip, port=port)

        # Override the process as a thread to handle the frame
        self._process = Thread(target=self._listen_high_level)

        # Initialise the frame-end string
        self._end_payload = bytes("Frame was successfully sent", encoding="ASCII")

        # Initialise the frame information
        self._frame = dumps(b'')

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, value):

        # Pickle the cv2 frame
        self._frame = dumps(value)

    def _handle_data(self):

        # Once connected, keep receiving and sending the data, raise exception in case of errors
        try:

            # Send the frame
            self._client_socket.sendall(self._frame)

            # Mark that the frame was sent
            self._client_socket.sendall(self._end_payload)

            # Wait for acknowledgement
            self._client_socket.recv(128)

        except (ConnectionResetError, ConnectionAbortedError, timeout):
            raise self.DataError

    def _on_surface_disconnected(self):

        # Close the socket
        self._client_socket.close()

        # Inform that the connection has been closed
        print("Video stream from {} address closed successfully".format(self._client_address))

    def run(self):

        # Start the video stream process
        self._process.start()
