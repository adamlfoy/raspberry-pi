"""

Server is used to handle the information exchange with high and low-level layers of the system.

** Functionality **

By importing the module you gain access to the classes 'Server' and 'Arduino'.

You should create an instance of 'Server' and use the 'run' function to start the communication. The constructor of the
'Server' class takes 2 optional parameters - 'ip' and 'port', which can be specified to identify address of the
Raspberry Pi (host) to connect with the surface. Ip passed should be a string, whereas the port an integer.

Once connected, the 'Server' class should handle everything, including formatting, encoding and re-connecting in case of
data loss. Exchanging data with the surface and each Arduino is done in separate processes.

You should modify the '_init_high_level' and '_init_low_level' functions to perform any additional initialisations of
the respective layers.

You should modify the '_listen_high_level' and '_listen_low_level' functions to change the existing ways of exchanging
information with the respective layers.

You should modify any `_handle_data` functions to change how the data is processed.

You should modify the '_on_surface_disconnected' function to modify behaviour when the connection between surface and
the Pi is lost. Remember, this function should always set the communication data to default using the 'data_manager'.

** Constants and other values **

All constants and other important values are mentioned and explained within the corresponding functions.

** Example **

Let ip be 169.254.147.140 and port 50000. To host a server with the given address, call:

    server = Server(ip=169.254.147.140)

The port is 50000 by default, so it's not necessary to explicitly specify it. To run, call:

    server.run()

** Author **

Kacper Florianski

"""

import socket
import communication.data_manager as dm
from serial import Serial, SerialException
from json import dumps, loads, JSONDecodeError
from time import sleep
from pathos import helpers

# Fetch the Process class
Process = helpers.mp.Process


class Server:

    # Custom exception to handle data errors
    class DataError(Exception):
        pass

    def __init__(self, *, ip='0.0.0.0', port=50000):
        """

        Function used to initialise the server.

        :param ip: Raspberry Pi's IP address
        :param port: Raspberry Pi's port

        """

        # Initialise communication with surface
        self._init_high_level(ip=ip, port=port)

        # Initialise communication with Arduino-s
        self._init_low_level(ports=["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"])

    def _init_high_level(self, ip, port):
        """

        Function used to initialise communication with the surface.

        ** Modifications **

            1. Modify the '_TIMEOUT' constant to specify the timeout value (seconds) for communication with the surface.

            2. Modify the try, except block to handle error messages when it's impossible to bind the socket.

        :param ip: Raspberry Pi's IP
        :param port: Raspberry Pi's port

        """

        # Initialise the process to handle parallel communication
        self._process = Process(target=self._listen_high_level)

        # Save the host and port information
        self._ip = ip
        self._port = port

        # Declare the constant for the communication timeout with the surface
        self._TIMEOUT = 3

        # Initialise the socket for IPv4 addresses (hence AF_INET) and TCP (hence SOCK_STREAM)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the given address, inform about errors
        try:
            self._socket.bind((self._ip, self._port))
        except socket.error:
            print("Failed to bind socket to the given address {}:{} ".format(self._ip, self._port))

        # Tell the server to listen to only one connection
        self._socket.listen(1)

    def _init_low_level(self, ports):
        """

        Function used to initialise communication with the surface.

        :param ports: An iterable of Arduino ports

        """

        # Declare a set of clients to remember
        self._clients = set()

        # Declare a list of ports to remember, match this with ids below for the overall initialisation
        self._ports = ports

        # Initialise an id list to assign a corresponding arduino to each port and a helper iterator
        arduino_ids = [dm.ARDUINO_T, dm.ARDUINO_A, dm.ARDUINO_M, dm.ARDUINO_I]

        # Iterate over each port and create corresponding clients
        for i in range(len(self._ports)):

            # Create an instance of the Arduino and store it
            self._clients.add(Arduino(self._ports[i], arduino_ids[i]))

    def _listen_high_level(self):
        """

        Function used to run a continuous connection with the surface.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking send and receive functions. The data exchanged is JSON-encoded.

        """

        # Never stop the server once it was started
        while True:

            # Inform that the server is ready to receive a connection
            print("{} is waiting for a client...".format(self._socket.getsockname()))

            # Wait for a connection (accept function blocks the program until a client connects to the server)
            self._client_socket, self._client_address = self._socket.accept()

            # Set a non-blocking connection to timeout on receive/send
            self._client_socket.setblocking(False)

            # Set the timeout
            self._client_socket.settimeout(self._TIMEOUT)

            # Inform that a client has successfully connected
            print("Client with address {} connected".format(self._client_address))

            while True:

                # Attempt to handle the data, break in case of errors
                try:
                    self._handle_data()
                except self.DataError:
                    break

            # Run clean up / connection lost info etc.
            self._on_surface_disconnected()

    def _listen_low_level(self):
        """

        Method used to run a continuous connection with the Arduino-s.

        The Arduino.connect function has a similar functionality to the _listen_high_level function, and is further
        described in ints corresponding documentation.

        """

        # Iterate over assigned clients
        for client in self._clients:
            client.connect()

    def _on_surface_disconnected(self):
        """

        Function used to clean up any resources or set appropriate flags when a connection to surface is closed.

        """

        # Close the socket
        self._client_socket.close()

        # Inform that the connection has been closed
        print("Connection from {} address closed successfully".format(self._client_address))

        # Set the keys to their default values, BEWARE: might add keys that haven't yet been received from surface
        dm.set_data(dm.SURFACE, **dm.DEFAULT)

    def _handle_data(self):
        """

        Function used to exchange and process the data.

        ** Modifications **

            1. Modify any try, except blocks to change the error-handling (keep in mind to use the DataError exception).

        """

        # Once connected, keep receiving and sending the data, raise exception in case of errors
        try:
            data = self._client_socket.recv(4096)

            # If 0-byte was received, close the connection
            if not data:
                raise self.DataError

        except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
            raise self.DataError

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
            self._client_socket.sendall(bytes(dumps(
                dm.get_data(dm.SURFACE, transmit=True)), encoding="utf-8"))

        except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
            raise self.DataError

    def run(self):
        """

        Function used to run the server.

        """

        # Start the communication with surface's process
        self._process.start()

        # Open the communication with lower-levels with the server's process as the parent process
        self._listen_low_level()


class Arduino:

    # Custom exception to handle data errors
    class DataError(Exception):
        pass

    def __init__(self, port, arduino_id):
        """

        Function used to initialise the state of each Arduino

        ** Modifications **

            1. Modify the '_WRITE_TIMEOUT' constant to specify the timeout value (seconds) for sending to an Arduino.

            2. Modify the '_READ_TIMEOUT' constant to specify the timeout value (seconds) for receiving from an Arduino.

            3. Modify the '_RECONNECT_DELAY' constant to specify the delay value (seconds) on connection loss.

            4. Modify the '_COMMUNICATION_DELAY' constant to specify the delay value (seconds) on communication.

        :param port: Raspberry Pi's port to which the Arduino is connected to
        :param arduino_id: Unique identifier of the Arduino
        """

        # Store the port information
        self._port = port

        # Store the id information
        self._id = arduino_id

        # Initialise custom baud rate constant (sorry if this is wrong Kacper :P )
        self._BAUD_RATE = 230400

        # Initialise the serial information
        self._serial = Serial()
        self._serial.port = self._port
        self._serial.baudrate = self._BAUD_RATE

        # Initialise the timeout constants
        self._WRITE_TIMEOUT = 1
        self._READ_TIMEOUT = 1

        # Set the read and write timeouts
        self._serial.write_timeout = self._WRITE_TIMEOUT
        self._serial.timeout = self._READ_TIMEOUT

        # Initialise the delay constant to offload some computing power
        self._RECONNECT_DELAY = 1

        # Initialise data exchange delay
        self._COMMUNICATION_DELAY = 0.02

        # Initialise the process information
        self._process = Process(target=self._run)

    def _handle_data(self):
        """

        Function used to exchange and process the data.

        ** Modifications **

            1. Modify any try, except blocks to change the error-handling (keep in mind to use the DataError exception).

        """

        # Send current state of the data
        self._serial.write(bytes(dumps(dm.get_data(self._id, transmit=True)) + "\n", encoding='utf-8'))

        # Read until the specified character is found ("\n" by default)
        data = self._serial.read_until()

        # Convert bytes to string, remove white spaces, ignore invalid data
        try:
            data = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            data = None

        # Handle valid data
        if data:

            try:
                # Attempt to decode the JSON data
                data = loads(data)

                # Override the ID
                self._id = data["deviceID"]

                # Update the Arduino data (and the surface data)
                dm.set_data(self._id, **data)

            except JSONDecodeError:
                print("Received invalid data: {}".format(data))
                raise self.DataError
            except KeyError:
                print("Received valid data with invalid ID: {}".format(data))
                raise self.DataError

        # Delay the communication to allow the Arduino to catch up
        sleep(self._COMMUNICATION_DELAY)

    def _run(self):
        """

        Function used to run a continuous connection with an Arduino.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking write and read_until functions. The data exchanged is JSON-encoded.

        """

        # Run an infinite loop to never close the connection
        while True:

            # Inform about a connection attempt
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

                # Attempt to handle the data, break in case of errors
                try:
                    self._handle_data()
                except self.DataError:
                    pass
                except SerialException:
                    print("Connection to port {} lost".format(self._port))
                    self._serial.close()
                    break

    def connect(self):
        """

        Function used to run the communication with an Arduino in a separate process.

        """

        # Start the connection
        self._process.start()
