"""

Data Manager is used to maintain different states of data across the system.

** Usage **

By importing the module you gain access to two global functions - 'get_data' and 'set_data'.

You should use the 'get_data' function to gain access to the available resources. You must specify the identifier, to
let the manager know which device should it change the data for. You may specify additional arguments, which should be
dictionary keys, to retrieve a part of the data. If no arguments are specified, the entire dictionary is returned.
The arguments passed should be strings (because the keys are stored as strings).

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

# Declare constants to easily access the resources
SURFACE = 0
ARDUINO_A = 1
ARDUINO_B = 2
ARDUINO_C = 3
ARDUINO_D = 4


class DataManager:

    def __init__(self):

        # Declare dictionaries of data
        self._surface = dict()
        self._arduino_A = dict()
        self._arduino_B = dict()
        self._arduino_C = dict()
        self._arduino_D = dict()

        # Create a dictionary mapping each index to corresponding location
        self._data = {
            SURFACE: self._surface,
            ARDUINO_A: self._arduino_A,
            ARDUINO_B: self._arduino_B,
            ARDUINO_C: self._arduino_C,
            ARDUINO_D: self._arduino_D
        }

    def get(self, index: int, *args):

        # Return selected data or whole dictionary if no args passed
        return {key: self._data[index][key] for key in args} if args else self._data[index]

    def set(self, index: int, **kwargs):

        # Update the data with the given keyword arguments
        for key, value in kwargs.items():
            self._data[index][key] = value


# Create a closure for the data manager
def _init_manager():

    # Create a free variable for the Data Manager
    d = DataManager()

    # Inner function to return the current state of the data
    def get_data(index: int, *args):
        return d.get(index, *args)

    # Inner function to alter the data
    def set_data(index: int, **kwargs):
        return d.set(index, **kwargs)

    return get_data, set_data


# Create globally accessible functions to manage the data
get_data, set_data = _init_manager()
