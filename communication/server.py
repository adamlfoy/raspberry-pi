import socket
from serial import Serial, SerialException
from multiprocessing import Process
from json import dumps, loads, JSONDecodeError

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

        try:
            # Bind the socket to the given address
            self._socket.bind((self._ip, self._port))
        except socket.error as e:
            print("Failed to bind socket to the given address {}:{} ".format(self._ip, self._port))

        # Tell the server to listen to only one connection
        self._socket.listen(1)

    # TODO: Finish this
    def _init_low_level(self):

        # Declare a set of clients to remember
        self._clients = set()

        # Declare a list of ports to remember
        self._ports = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"]

        # Iterate over each port and create corresponding clients
        for port in self._ports:

            try:
                # Create an instance of the Arduino and store it
                self._clients.add(Arduino(port))
                print("Connection with {} established.".format(port))

            except SerialException:
                print("Failed to connect to {}".format(port))

    def _listen_high_level(self):

        # Never stop the server once it was started
        while True:

            # Inform that the server is ready to receive a connection
            print("Waiting for a connection...")

            # Wait for a connection (accept function blocks the program until a client connects to the server)
            self._client_socket, self._client_address = self._socket.accept()

            # Inform that someone has connected
            print("Client with address {} connected".format(self._client_address))

            while True:

                try:
                    # Once connected, keep receiving and sending the data, break in case of errors
                    data = self._client_socket.recv(4096)

                    # If 0-byte was received, close the connection
                    if not data:
                        break

                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break

                # Convert bytes to string, remove white spaces, ignore invalid data
                try:
                    data = data.decode("utf-8").strip()
                except UnicodeDecodeError:
                    data = None

                # Handle valid data
                if data:

                    # Attempt to decode from JSON, inform about invalid data received
                    try:
                        dm.data.set(dm.SURFACE, **loads(data))
                    except JSONDecodeError:
                        print("Received invalid data: {}".format(data))

                # Send current state of the data manager
                self._client_socket.sendall(bytes(dumps(dm.data.get(dm.SURFACE)), encoding="utf-8"))

            # Clean up
            self._client_socket.close()

            # Inform that the connection is closed
            print("Connection from {} address closed successfully".format(self._client_address))

    # TODO: Finish this
    def _listen_low_level(self):

        # Never stop the server once it was started
        while True:
            pass

    # TODO: Finish this, possibly use threads and/or spawn more processes
    def run(self):

        # Run each connection
        Process(target=self._listen_high_level).start()


# TODO: Finish this
class Arduino:

    # TODO: Finish this
    def __init__(self, port):

        # Create a new serial object
        self._serial = Serial(port)

    # TODO: Finish this
    def _run(self):

        # Run an infinite loop to keep exchanging data
        while True:
            pass


if __name__ == "__main__":
    s = Server()
    s.run()
