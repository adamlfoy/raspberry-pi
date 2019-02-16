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

        # Iterate over assigned clients
        for client in self._clients:
            client.connect()

    def run(self):

        # Open the communication with surface in a new process
        Process(target=self._listen_high_level).start()

        # Open the communication with lower-levels with the server's process as the parent process
        self._listen_low_level()


# TODO: Finish this
class Arduino:

    def __init__(self, port, arduino_id):

        # Store the port information
        self._port = port

        # Store the id information
        self._id = arduino_id

        # Initialise the serial information
        self._serial = Serial()
        self._serial.port = self._port

        # Initialise the process information
        self._process = Process(target=self._run)

        # Initialise the delay constant to offload some computing power
        self._RECONNECT_DELAY = 1

        # Initialise data exchange delay
        self._COMMUNICATION_DELAY = 0.02

    # TODO: Finish this, test this, secure against errors (incl. connection loss on both sides)
    def _run(self):

        # Run an infinite loop to never close the connection
        while True:

            # Inform about connection attempt
            print("Connecting to port {}...".format(self._port))

            # Keep attempting to establish a connection
            while True:

                try:
                    # Attempt to assign a serial connection
                    self._serial.open()

                except SerialException:
                    sleep(self._RECONNECT_DELAY)
                    continue

                # Inform about successfully established connection
                print("Successfully connected to port {}".format(self._port))

                try:
                    if self._serial.is_open:  # TODO: Check if this is even needed with try-except block

                        # Send current state of the data
                        self._serial.write(bytes(dumps(dm.get_data(self._id))))

                        # Read until the specified character is found
                        data = self._serial.read_until()  # TODO: Find out if 0-byte is send on connection close

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

                    else:
                        print("Connection to port {} lost".format(self._port))
                        self._serial.close()
                        break

                except SerialException:
                    print("Connection to port {} lost".format(self._port))
                    self._serial.close()
                    break

                except TypeError:
                    print("test to see what causes this, possibly None-s")  # TODO <--
                    pass

    def connect(self):

        # Start the connection
        self._process.start()


if __name__ == "__main__":
    s = Server()
    s.run()
