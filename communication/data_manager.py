from collections.abc import MutableMapping


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
