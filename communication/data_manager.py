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

    # Create a free variable for the Data Manager TODO: Make it a singleton
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