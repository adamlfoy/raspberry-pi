"""

Video Stream is used to handle the visual data exchange with surface.

** Functionality **

By importing the module you gain access to the class 'VideoStream'.

You should create an instance of 'VideoStream' and use the 'run' function to start the communication. The constructor of
takes 2 optional parameters - 'ip' and 'port', which can be specified to identify the address of the Raspberry Pi (host)
to connect with the surface. Ip passed should be a string, whereas the port an integer.

Once connected, the class should handle everything, including formatting, encoding and re-connecting in case of
data loss. Additionally, the class allows you to access and set the frame through the 'frame' field.

You should modify any `_handle_data` functions to change how the data is processed.

You should modify the '_on_surface_disconnected' function to modify behaviour when the connection between surface and
the PI is lost. Remember, this function should always set the communication data to default using the 'data_manager'.

** Constants and other values **

All constants and other important values are mentioned and explained within the corresponding functions.

** Example **

Let ip be 169.254.147.140 and port 50001. To host a stream with the given address, call:

    video_stream = VideoStream(ip=169.254.147.140)

The port is 50001 by default, so it's not necessary to explicitly specify it. To run, call:

    video_stream.run()

Let frame be a cv2 numpy array. To send it, call

    video_stream.frame = frame

** Author **

Kacper Florianski

"""

from communication.server import Server
from dill import dumps
from socket import timeout
from threading import Thread


class VideoStream(Server):

    def __init__(self, ip="localhost", port=50001):
        """

        Function used to initialise the stream.

        :param ip: Raspberry Pi's IP address
        :param port: Raspberry Pi's port

        """

        # Super the TCP data exchange functionality
        super()._init_high_level(ip=ip, port=port)

        # Override the process as a thread to handle the frame correctly
        self._process = Thread(target=self._listen_high_level)

        # Initialise the frame-end string to mark when a full frame was sent
        self._end_payload = bytes("Frame was successfully sent", encoding="ASCII")

        # Initialise the frame
        self._frame = dumps(b'')

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, value):

        # Pickle the cv2 frame
        self._frame = dumps(value)

    def _handle_data(self):
        """

        Function used to exchange and process the frames.

        """

        # Once connected, keep receiving and sending the data, raise exception in case of errors
        try:

            # Send the frame
            self._client_socket.sendall(self._frame)

            # Mark that the frame was sent
            self._client_socket.sendall(self._end_payload)

            # Wait for the acknowledgement
            self._client_socket.recv(128)

        except (ConnectionResetError, ConnectionAbortedError, timeout):
            raise self.DataError

    def _on_surface_disconnected(self):
        """

        Function used to clean up any resources or set appropriate flags when a connection to surface is closed.

        """

        # Close the socket
        self._client_socket.close()

        # Inform that the connection has been closed
        print("Video stream from {} address closed successfully".format(self._client_address))

    def run(self):
        """

        Function used to run the stream.

        """

        # Start the video stream process
        self._process.start()
