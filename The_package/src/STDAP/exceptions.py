"""
    This file contains all exceptions used in the python package.
    List of exceptions:
    - Initializing_error
"""


class Initializing_error(Exception):
    """
        This error is called when a simulation is called without the information
        it needs. Most likely: choose city has not been called.
    """
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return str(self.message)
