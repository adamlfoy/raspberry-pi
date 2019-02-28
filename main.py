# TODO: Fix relative path issues on PI (after adding the server to run on boot)
# TODO: Fix data formatting issue between Arduinos and PI
# TODO: Add ID exchange between Arduinos and PI
# TODO: If solution found, replace argumented server with data manager module imports

import communication.data_manager as dm
from communication.server import Server

if __name__ == "__main__":
    s = Server(dm)
    s.run()
