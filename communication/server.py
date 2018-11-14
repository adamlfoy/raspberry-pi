from communication.data_manager import DataStorage
from threading import Thread
import socket


class Server:

    def __init__(self, *, ip='0.0.0.0', port=50000):

        # Save the host and port information
        self.ip = ip
        self.port = port

        # Declare clients storage
        self._clients = list()

        # Declare data storage
        self._data = DataStorage

        # Initialise the socket for IPv4 addresses (hence AF_INET) and TCP (hence SOCK_STREAM)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Bind the socket to the given address
            self._socket.bind((self.ip, self.port))
        except socket.error as e:
            print("Failed to bind socket to the given ip and port - " + str(e))
            exit(0)

    def _listen(self):

        # Allow 3 connections queued up at the same time
        self._socket.listen(3)

        print("Accepting connections to {0} on port {1}".format(self.ip, self.port))

        # Keep accepting new clients
        while True:

            # Retrieve the socket, and address from the connected client
            client, address = self._socket.accept()
            print("New client with address {0}:{1} connected.".format(address[0], address[1]))

            # Send a welcome message
            client.sendall(bytes("Hello there, general {0}\r\n".format(address), encoding="UTF-8"))

            # Remember the client
            self._clients.append(Client(client, address))

    def _cleanup(self):

        # Keep cleaning up
        while True:

            # Iterate over clients to remove inactive connections
            for client in self._clients:
                if not client.thread:
                    self._clients.remove(client)

    def __call__(self):

        # Listen to new connections
        Thread(target=self._listen).start()

        # Keep cleaning up the resources
        Thread(target=self._cleanup).start()


class Client:

    def __init__(self, client, address):

        # Assign data passed from the accept() method
        self._socket = client
        self._address = address

        # Declare constant for the timeout
        self._TIMEOUT = 3

        # Specify the timeout to get rid of... timeouts, and shut the connection
        self._socket.settimeout(self._TIMEOUT)

        # Declare constant for the size of buffer
        self._BUFFER = 4096

        # Initialise the data storage
        self._data = None

        # Create a new thread and run it
        self._thread = Thread(target=self._run)
        self._thread.start()

    @property
    def data(self):
        return self._data

    @property
    def thread(self):
        return self._thread.is_alive()

    def _run(self):

        # An infinite loop, has a break clause inside
        while True:

            # Get new data
            try:
                # Once connected, keep receiving the data, break in case of errors
                data = self._socket.recv(self._BUFFER)
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
                break
            except socket.timeout:
                break

            # If 0-byte was received, close the connection
            if not data:
                break
            else:
                print("{0} - {1}".format(self, data))

        # Release resources
        self._socket.close()
        print("Client {0} disconnected.".format(self))

    def __str__(self):
        return "{0}:{1}".format(self._address[0], self._address[1])


if __name__ == "__main__":
    Server()()
