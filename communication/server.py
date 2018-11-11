from collections.abc import MutableMapping
import socket


class Server:

    # TODO: Finish the __init__ method with all other, necessary init information
    # TODO: Come up with a way to neatly recognise different clients
    def __init__(self, *, ip='0.0.0.0', port=50000):

        # Save the host and port information
        self.ip = ip
        self.port = port

        # Declare clients storage
        self.clients = dict()

        # Initialise the socket for IPv4 addresses (hence AF_INET) and TCP (hence SOCK_STREAM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Bind the socket to the given address
            self.socket.bind((self.ip, self.port))
        except socket.error as e:
            print("Failed to bind socket to the given ip and port - " + str(e))
            exit(0)

        # Allow 3 connections queued up at the same time
        self.socket.listen(3)

    # TODO: Check if the resources for new clients must be manually cleaned once connection lost
    # TODO: Spawn a new process / thread handling communication with each client
    # TODO: Write functionality, method should add each client to the clients dictionary, with unique ID
    def add_client(self, data):
        pass

    # TODO: Write a method that collects data from each client, possibly call client's method
    def receive(self):
        pass

    # TODO: Write a method that sends formatted data to a chosen client, possibly call client's method
    def send(self, data, target):
        pass


class Client:

    # TODO: Fill in the Client class, possibly add data receiving, send methods etc.
    def __init__(self, data):
        """The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data
        on the connection, and address is the address bound to the socket on the other end of the connection"""
        pass

# TO READ
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