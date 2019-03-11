"""

Data Manager is used to maintain different states of data across the system.

** Usage **

By importing the module you gain access to two global functions - 'get_data' and 'set_data'.

You should use the 'get_data' function to gain access to the available resources. You must specify the identifier, to
let the manager know which device should it change the data for. You may specify additional arguments, which should be
dictionary keys, to retrieve a part of the data. If no arguments are specified, the entire dictionary is returned.
The arguments passed should be strings (because the keys are stored as strings).

Set the additional 'transmit' keyword argument when retrieving the data, if the dictionary returned should only contain
the fields that should be sent over the network. Each item to be sent over the network must be specified in the
'_transmission_keys' set within the class, and agreed with the lower-level team beforehand. Set the argument to True to
retrieve such data. The base functionality otherwise stays the same as with the argument being (by default) False.

You should use the 'set_data' function to change the resources. You must specify the identifier, to let the manager know
which device should it change the data for. For each keyword argument passed, the state of the data dictionary under the
given key will be changed to the given value.

** Example **

Let axis_x = 10, axis_y = 20, axis_z = -15. To save these values as surface readings into the data manager, call:

    set_data(SURFACE, axis_x=10, axis_y=20, axis_z=-15)

To retrieve the information about axis x and y, call:

    data = get_data(SURFACE, 'axis_x', 'axis_y')

The result of printing data is as follows:

    {'axis_x': 10, 'axis_y': 20}

** Author **

Kacper Florianski

"""

from diskcache import FanoutCache
from os import path

# Declare constants to easily access the resources
SURFACE = 0
ARDUINO_T = "Ard-T"
ARDUINO_A = "Ard-A"
ARDUINO_M = "Ard-M"
ARDUINO_I = "Ard-I"


class DataManager:

    def __init__(self):

        # Declare dictionaries of data
        self._surface = FanoutCache(path.join("cache", "surface.cache"), shards=2)
        self._arduino_T = FanoutCache(path.join("cache", "arduino_t.cache"), shards=2)
        self._arduino_A = FanoutCache(path.join("cache", "arduino_a.cache"), shards=2)
        self._arduino_M = FanoutCache(path.join("cache", "arduino_m.cache"), shards=2)
        self._arduino_I = FanoutCache(path.join("cache", "arduino_i.cache"), shards=2)

        # Create a dictionary mapping each index to corresponding location
        self._data = {
            SURFACE: self._surface,
            ARDUINO_T: self._arduino_T,
            ARDUINO_A: self._arduino_A,
            ARDUINO_M: self._arduino_M,
            ARDUINO_I: self._arduino_I
        }

        # Create a dictionary mapping each index to a set of networking keys
        self._transmission_keys = {
            SURFACE: {"example"},
            ARDUINO_T: {"Thr-FP", "Thr-FS", "Thr-AP", "Thr-AS", "Thr-TFP", "Thr-TFS", "Thr-TAP", "Thr-TAS"},
            ARDUINO_A: {"Mot-R", "Mot-G", "Mot-F"},
            ARDUINO_M: {"Thr-M", "LED-M"},
            ARDUINO_I: {"Sen-IMU", "Sen-Dep", "Sen-Temp", "Sen-Leak"}
        }

    def get(self, index: int, *args, transmit=False):

        # If the data retrieved is meant to be sent over the network
        if transmit:

            # Return selected data or transmission-specific dictionary if no args passed
            return {key: self._data[index][key] for key in args if key in self._transmission_keys[index]} if args else \
                {key: self._data[index][key] for key in self._transmission_keys[index] if key in self._data[index]}

        # Return selected data or whole dictionary if no args passed
        return {key: self._data[index][key] for key in args} if args else {key: self._data[index][key]
                                                                           for key in self._data[index]}

    # TODO: Try to optimise this function ( O(n^2) :( )
    def set(self, index: int, **kwargs):

        # If index passed is surface
        if index == SURFACE:

            # Update the surface data with the given keyword arguments
            for key, value in kwargs.items():
                self._data[SURFACE][key] = value

            # Dispatch the Arduino values
            for index, values in self._transmission_keys.items():
                if index != SURFACE:

                    # Iterate over all keys in the transmission set
                    for key in values:

                        # Check if the key is in the data passed
                        if key in self._data[SURFACE]:

                            # Update the according value
                            self._data[index][key] = self._data[SURFACE][key]

        # If index passed is an Arduino
        else:

            # Update the data with the given keyword arguments, and update the surface anyway
            for key, value in kwargs.items():
                self._data[index][key] = value
                self._data[SURFACE][key] = value

    def clear(self):
        self._surface.clear()
        self._arduino_T.clear()
        self._arduino_A.clear()
        self._arduino_M.clear()
        self._arduino_I.clear()


# Create a closure for the data manager
def _init_manager():

    # Create a free variable for the Data Manager
    d = DataManager()

    # Inner function to return the current state of the data
    def get_data(index: int, *args, transmit=False):
        return d.get(index, *args, transmit=transmit)

    # Inner function to alter the data
    def set_data(index: int, **kwargs):
        return d.set(index, **kwargs)

    # Inner function to clear the cache
    def clear():
        d.clear()

    return get_data, set_data, clear


# Create globally accessible functions to manage the data
get_data, set_data, clear = _init_manager()
