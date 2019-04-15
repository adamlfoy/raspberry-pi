"""

Data Manager is used to maintain different states of data across the system.

** Functionality **

By importing the module you gain access to three global functions - 'get_data', 'set_data' and 'clear'.

You should use the 'get_data' function to gain access to the available resources. You must specify the identifier, to
let the manager know which device should it change the data for. You may specify additional arguments, which should be
dictionary keys, to retrieve a part of the data. If no arguments are specified, the entire dictionary is returned.
The arguments passed should be strings (because the keys are stored as strings).

Set the additional 'transmit' keyword argument when retrieving the data, if the dictionary returned should only contain
the fields to be sent over the network. Dictionary keys of values to be sent over the network must be included in the
'_transmission_keys' set within the class, and agreed with the lower-level team beforehand. Set the argument to True to
retrieve such data. The base functionality otherwise stays the same as with the argument being (by default) False.

You should use the 'set_data' function to change the resources. You must specify the identifier, to let the manager know
which device should it change the data for. For each keyword argument passed, the state of the data dictionary under the
given key will be changed to the given value.

You should use the 'clear' function to clear the cache (for example at start of the program) to save some memory.

** Constants and other values **

Additionally, you should modify existing constants to change the behaviour of the data manager.

You should modify the 'SURFACE', 'ARDUINO_T', ... constants to change the identifier of each device. Naturally, the
values assigned to these constants must be unique.

You should modify the 'DEFAULT' constant to change the default connection loss values. This data will simulate receiving
such values from the surface and can be used to specify custom behaviour on losing the connection (e.g. thrusters off).

As mentioned before, you should modify the '_transmission_keys' set to include all the values that should be networked
with the surface or Arduino-s.

** Example **

Let axis_x = 10, axis_y = 20, axis_z = -15. To save these values as surface readings into the data manager, call:

    set_data(SURFACE, axis_x=10, axis_y=20, axis_z=-15)

To retrieve the information about axis x and y, call:

    data = get_data(SURFACE, 'axis_x', 'axis_y')

The result of printing 'data' is as follows:

    {'axis_x': 10, 'axis_y': 20}

** Author **

Kacper Florianski

"""

from diskcache import FanoutCache
from os import path

# Declare constants to easily access the resources
SURFACE = 0
ARDUINO_T = "Ard_T"
ARDUINO_A = "Ard_A"
ARDUINO_M = "Ard_M"
ARDUINO_I = "Ard_I"

# Declare some default values
THRUSTER_IDLE = 1500
LIGHT_OFF = 1100

# Declare default key, value pairs to handle connection loss with surface
DEFAULT = {
    "Thr_FP": THRUSTER_IDLE,
    "Thr_FS": THRUSTER_IDLE,
    "Thr_AP": THRUSTER_IDLE,
    "Thr_AS": THRUSTER_IDLE,
    "Thr_TFP": THRUSTER_IDLE,
    "Thr_TFS": THRUSTER_IDLE,
    "Thr_TAP": THRUSTER_IDLE,
    "Thr_TAS": THRUSTER_IDLE,
    "Mot_R": THRUSTER_IDLE,
    "Mot_G": THRUSTER_IDLE,
    "Mot_F": THRUSTER_IDLE,
    "LED_M": LIGHT_OFF
}


class DataManager:

    def __init__(self):
        """

        Function used to initialise the data manager.

        ** Modifications **

            1. Modify the '_transmission_keys' set to specify which values should be transmitted to each component.

        """

        # Declare dictionaries of data
        self._surface = FanoutCache(path.join("cache", "surface"), shards=2)
        self._arduino_T = FanoutCache(path.join("cache", "arduino_t"), shards=2)
        self._arduino_A = FanoutCache(path.join("cache", "arduino_a"), shards=2)
        self._arduino_M = FanoutCache(path.join("cache", "arduino_m"), shards=2)
        self._arduino_I = FanoutCache(path.join("cache", "arduino_i"), shards=2)

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
            SURFACE: {"status_T", "status_A", "status_M", "status_I", "error_T", "error_A", "error_M", "error_I",
                      "Sen_IMU_X", "Sen_IMU_Y", "Sen_IMU_Z", "Sen_IMU_Temp"},
            ARDUINO_T: {"Thr_FP", "Thr_FS", "Thr_AP", "Thr_AS", "Thr_TFP", "Thr_TFS", "Thr_TAP", "Thr_TAS"},
            ARDUINO_A: {"Mot_R", "Mot_G", "Mot_F"},
            ARDUINO_M: {"Thr_M", "LED_M"},
            ARDUINO_I: {}
        }

        # Create a key to ID lookup for performance reasons
        self._keys_lookup = {v: k for k, values in self._transmission_keys.items() if k != SURFACE for v in values}

    def get(self, index: int, *args, transmit=False):
        """

        Function used to access the cache.

        Returns full dictionary if no args passed, or partial data if either args are passed or transmit is set to True.

        :param index: Device index to retrieve the data from
        :param args: Keys to retrieve
        :param transmit: Boolean to specify if the transmission-only data should be retrieved
        :return: Data stored in the data manager

        """

        # If the data retrieved is meant to be sent over the network
        if transmit:

            # Return selected data or transmission-specific dictionary if no args passed
            return {key: self._data[index][key] for key in args if key in self._transmission_keys[index]} if args else \
                {key: self._data[index][key] for key in self._transmission_keys[index] if key in self._data[index]}

        # Return selected data or whole dictionary if no args passed
        return {key: self._data[index][key] for key in args} if args else {key: self._data[index][key]
                                                                           for key in self._data[index]}

    def set(self, index: int, **kwargs):
        """

        Function used to modify the cache.

        :param index: Device index to retrieve the data from
        :param kwargs: Key, value pairs of data to modify.

        """

        # Iterate over all kwargs' key, value pairs
        for key, value in kwargs.items():

            # If index passed is Surface
            if index == SURFACE:

                # Update the corresponding Arduino transmission data
                if key in self._keys_lookup:
                    self._data[self._keys_lookup[key]][key] = value

                # Update the surface data
                self._data[SURFACE][key] = value

            # If index passed is an Arduino
            else:

                # Update the corresponding Arduino data
                self._data[index][key] = value

                # Update the corresponding Surface transmission data
                if key in self._data[SURFACE]:
                    self._data[SURFACE][key] = value

    def clear(self):
        """

        Function used to clear the cache.

        """

        self._surface.clear()
        self._arduino_T.clear()
        self._arduino_A.clear()
        self._arduino_M.clear()
        self._arduino_I.clear()


# Create a closure for the data manager
def _init_manager():
    """

    Function used to create a closure for the data manager.

    :return: Enclosed functions

    """

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
