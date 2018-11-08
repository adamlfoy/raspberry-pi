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
    # TODO: Add data storage???
    def __init__(self, data):
        """The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data
        on the connection, and address is the address bound to the socket on the other end of the connection"""
        pass

# TO READ
# https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
