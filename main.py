# TODO: Fix relative path issues on PI (after adding the server to run on boot)

import communication.data_manager as dm
from communication.server import Server


if __name__ == "__main__":

    # Clear the cache on start
    dm.clear()

    # Initialise the server
    s = Server()

    # Start the tasks
    s.run()
