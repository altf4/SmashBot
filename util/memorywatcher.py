#!/usr/bin/python3

import binascii
import os
import socket
from util import paths

class MemoryWatcher:
    """Reads and parses game memory changes.
    Pass the location of the socket to the constructor, then either manually
    call next() on this class to get a single change, or else use it like a
    normal iterator.
    """
    def __init__(self):
        """Creates the socket if it does not exist, and then opens it."""
        path = paths.get_memory_watcher_socket_path()
        try:
            os.unlink(path)
        except OSError:
            pass
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(path)

    def __iter__(self):
        """Iterate over this class in the usual way to get memory changes."""
        return self

    def __del__(self):
        """Closes the socket."""
        self.sock.close()

    def __next__(self):
        """Returns the next (address, value) tuple, or None on timeout.
        address is the string provided by dolphin, set in Locations.txt.
        value is a four-byte string suitable for interpretation with struct.
        """
        try:
            data = self.sock.recvfrom(4096)[0].decode('utf-8').splitlines()
        except socket.timeout:
            return None
        # Strip the null terminator, pad with zeros, then convert to bytes
        return data[0], binascii.unhexlify(data[1].strip('\x00').zfill(8))
