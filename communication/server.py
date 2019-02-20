"""

Server is used to handle the information exchange with the Raspberry Pi.

** Usage **

By importing the module you gain access to the classes 'Server' and 'Arduino'.

You should create an instance of it and use the 'run' function to start the communication.The constructor of the
'Server' class takes 2 optional parameters - 'ip' and 'port', which can be specified to identify address of the
Raspberry Pi (host) for connecting with the surface. Ip passed should be a string, whereas the port an integer. Both
arguments are of the keyword-only type.

Once connected, the 'Server' class should handle everything, including formatting, encoding and re-connecting in case of
data loss. Exchanging data with the surface and each Arduino is done in a separate process.

** Example **

Let ip be 169.254.147.140 and port 50000. To host a server with the given address, call:

    server = Server(ip=169.254.147.140)

The port is 50000 by default, so it's not necessary to explicitly specify it. To run, call:

    server.run()

** Author **

Kacper Florianski

"""

import socket
from serial import Serial, SerialException
from multiprocessing import Process
from json import dumps, loads, JSONDecodeError
from time import sleep

# TODO: Fix relative path issues on PI (after adding the server to run on boot)
import communication.data_manager as dm


class Server:

    def __init__(self, *, ip='0.0.0.0', port=50000):

        # Initialise communication with surface
        self._init_high_level(ip, port)

        # Initialise communication with Arduino-s
        self._init_low_level()

    def _init_high_level(self, ip, port):

        # Save the host and port information
        self._ip = ip
        self._port = port

        # Initialise the socket for IPv4 addresses (hence AF_INET) and TCP (hence SOCK_STREAM)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Declare the constant for the communication timeout with the surface
        self._TIMEOUT = 3

        # Bind the socket to the given address, inform about errors TODO: Add binding into loop
        try:
            self._socket.bind((self._ip, self._port))
        except socket.error:
            print("Failed to bind socket to the given address {}:{} ".format(self._ip, self._port))

        # Tell the server to listen to only one connection
        self._socket.listen(1)

    def _init_low_level(self):

        # Declare a set of clients to remember
        self._clients = set()

        # Declare a list of ports to remember
        self._ports = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"]

        # Initialise an id iterator to assign a corresponding arduino to each port
        arduino_id = 1

        # Iterate over each port and create corresponding clients
        for port in self._ports:

            # Create an instance of the Arduino and store it
            self._clients.add(Arduino(port, arduino_id))

            # Pick next identification to assign
            arduino_id += 1

    def _listen_high_level(self):
        """

        Method used to run a continuous connection with the surface.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking send and receive functions. The data exchanged is JSON-encoded.

        """

        # Never stop the server once it was started
        while True:

            # Inform that the server is ready to receive a connection
            print("Waiting for a connection from the surface...")

            # Wait for a connection (accept function blocks the program until a client connects to the server)
            self._client_socket, self._client_address = self._socket.accept()

            # Set a non-blocking connection to timeout on receive/send
            self._client_socket.setblocking(False)

            # Set the timeout
            self._client_socket.settimeout(self._TIMEOUT)

            # Inform that a client has successfully connected
            print("Client with address {} connected".format(self._client_address))

            while True:

                # Once connected, keep receiving and sending the data, break in case of errors
                try:
                    data = self._client_socket.recv(4096)

                    # If 0-byte was received, close the connection
                    if not data:
                        break

                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break
                except socket.timeout:
                    break

                # Convert bytes to string, remove the white spaces, ignore any invalid data
                try:
                    data = data.decode("utf-8").strip()
                except UnicodeDecodeError:
                    data = None

                # Handle valid data
                if data:

                    # Attempt to decode from JSON, inform about invalid data received
                    try:
                        dm.set_data(dm.SURFACE, **loads(data))
                    except JSONDecodeError:
                        print("Received invalid data: {}".format(data))

                # Send the current state of the data manager, break in case of errors
                try:
                    self._client_socket.sendall(bytes(dumps(dm.get_data(dm.SURFACE)), encoding="utf-8"))

                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break
                except socket.timeout:
                    break

            # Clean up
            self._client_socket.close()

            # Inform that the connection has been closed
            print("Connection from {} address closed successfully".format(self._client_address))

    def _listen_low_level(self):
        """

        Method used to run a continuous connection with the Arduino-s.

        The Arduino.connect function has a similar functionality to the _listen_high_level function, and is further
        described in ints corresponding documentation.

        """

        # Iterate over assigned clients
        for client in self._clients:
            client.connect()

    def run(self):

        # Open the communication with surface in a new process
        Process(target=self._listen_high_level).start()

        # Open the communication with lower-levels with the server's process as the parent process
        self._listen_low_level()


# TODO: Test and resolve possible problems with incorrect port assignments. Possibly make a pre-communication
# TODO: ping exchange, to identify which arduino is connected to which port. Test with proper Arduino code.
class Arduino:

    def __init__(self, port, arduino_id):

        # Store the port information
        self._port = port

        # Store the id information
        self._id = arduino_id

        # Initialise the serial information
        self._serial = Serial()
        self._serial.port = self._port

        # Initialise the timeout constants
        self._WRITE_TIMEOUT = 5
        self._READ_TIMEOUT = 5

        # Set the read and write timeouts
        self._serial.write_timeout = self._WRITE_TIMEOUT
        self._serial.timeout = self._READ_TIMEOUT

        # Initialise the delay constant to offload some computing power
        self._RECONNECT_DELAY = 1

        # Initialise data exchange delay
        self._COMMUNICATION_DELAY = 0.02

        # Initialise the process information
        self._process = Process(target=self._run)

    def _run(self):

        # Run an infinite loop to never close the connection
        while True:

            # Inform about connection attempt
            print("Connecting to port {}...".format(self._port))

            # Keep exchanging the data or re-connecting
            while True:

                # If the connection is closed
                if not self._serial.is_open:

                    try:
                        # Attempt to open a serial connection
                        self._serial.open()

                        # Inform about a successfully established connection
                        print("Successfully connected to port {}".format(self._port))

                    except SerialException:
                        sleep(self._RECONNECT_DELAY)
                        continue

                try:
                    # Send current state of the data
                    self._serial.write(bytes(dumps(dm.get_data(self._id)), encoding='utf-8'))

                    # Read until the specified character is found ("\n" by default)
                    data = self._serial.read_until()

                    # Convert bytes to string, remove white spaces, ignore invalid data
                    try:
                        data = data.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        data = None

                    # Handle valid data
                    if data:

                        # Attempt to decode from JSON, inform about invalid data received
                        try:
                            dm.set_data(self._id, **loads(data))
                        except JSONDecodeError:
                            print("Received invalid data: {}".format(data))

                    # Delay the communication to allow the Arduino to catch up
                    sleep(self._COMMUNICATION_DELAY)

                except SerialException:
                    print("Connection to port {} lost".format(self._port))
                    self._serial.close()
                    break

    def connect(self):
        """

        Method used to run a continuous connection with the surface.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking write and read_until functions. The data exchanged is JSON-encoded.

        """

        # Start the connection
        self._process.start()


if __name__ == "__main__":
    s = Server()
    s.run()
