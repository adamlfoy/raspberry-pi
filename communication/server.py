from collections.abc import MutableMapping
from threading import Thread
import socket


class Server:

    # TODO: self._data -> (ID, dict) - Clients will have to send JSON with specific id to successfully get added
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

    # TODO: Check if the resources for new clients must be manually cleaned once connection lost
    # TODO: Actually write the thing... error checking, logging etc. etc.
    # TODO: Possibly rename this to __call__, so you can say s = Server(); s()
    def listen(self):

        # Allow 3 connections queued up at the same time
        self._socket.listen(3)

        # Keep accepting new clients
        while True:

            client, address = self._socket.accept()
            client.sendall(bytes("Hello there, general {0}\r\n".format(address), encoding="UTF-8"))
            self._clients.append(Client(client, address))

    # TODO: Write a neat sendall with /r/n breaks for telnet testing
    def send(self, client):
        pass


class Client:

    def __init__(self, client, address):

        # Assign data passed from the accept() method
        self._socket = client
        self._address = address

        # Specify the timeout to get rid of... timeouts, and shut the connection
        self._socket.settimeout(10)

        # Declare constant for the size of buffer
        self._BUFFER = 4096

        # Initialise the data storage
        self._data = None

        # Create a new thread and run it
        self._thread = Thread(target=self.run)
        self._thread.start()

    @property
    def data(self):
        return self._data

    # Function that keeps receiving the data
    # TODO: Add proper running, error checking, write to exceptions, logging (prints) etc.
    def run(self):

        # An infinite loop, has a break clause inside
        while True:

            # Get new data
            try:
                data = self._socket.recv(self._BUFFER)
                if data:
                    print(data)
                else:
                    raise socket.error('Client disconnected')
            except:
                self._socket.close()
                break

    # TODO: Possibly add better __str__, and implement __repr__ if needed
    def __str__(self):
        return "Ip: {0}, Port {1}".format(self._address[0], self._address[1])


# TODO: READ (Already read, include as reference, was helpful
# https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client


class DataStorage:
    """
    Class handling addition, retrieval and modification of data.

    -= Getting data =-

    To retrieve existing data, call an instance of this object with a valid key value (must be str).
    The stored data will be returned on success, None otherwise.
    Example: storage("existing_key") where storage is an instance of DataStorage.

    -= Setting data =-

    To add new data, call an instance of this object with a unique key value (must be str) and data (must be a mapping).
    True will be returned on successful addition, False otherwise.
    Example: storage("new_key", data) where storage is an instance of DataStorage, and data is a mutable mapping type.

    -= Modifying data =-

    To modify existing data, call the modify method with a valid key value and key, value pairs of data to be changed.
    True will be returned on successful modification, False otherwise.
    Example: storage.modify("existing_key", "key1"=1, "key2"=2) where storage is an instance of DataStorage.
    """

    def __init__(self):

        # Declare a dictionary to store data
        self._data = dict()

    def __call__(self, key: str, *, data=None):

        # Check the key's type
        if not type(key) == str:
            raise TypeError

        # Check for a valid "get" request, return None on invalid key
        if data is None:
            return self._data[key] if key in self._data else None

        # Check the data's type
        if not isinstance(data, MutableMapping):
            raise TypeError

        # Check for a valid "set" request, return True on success, False on failure
        if key not in self._data:
            self._data[key] = data
            return True
        else:
            return False

    def modify(self, key, **kwargs):

        # Check the key's type
        if not type(key) == str:
            raise TypeError

        # Check for a valid "get" request
        if key in self._data:

            # Iterate over requested pairs and change data for each valid one
            for k, v in kwargs.items():
                self._data[key][k] = v

            return True
        else:
            return False

# TODO: Write a decorator to debug any class - fields + functions + call time + call location (module maybe? or outer scope)

s = Server()
s.listen()

'''
TODO: Remove it, possibly create proper assertion tests

d = DataStorage()
x = {
    'a': 2,
    'b': 0
}
print(d("x", data=x))
print(d("x", data=dict()))
print(d("x"))
print(d("u"))
print(d.modify("x", c=4))
print(d.modify("x", a=20, b=10))
print(d.modify("u", c=4))
print(d("x"))
print(d("u"))
'''