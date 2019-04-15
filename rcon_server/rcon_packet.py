# Packet types

from util import to_int32

class RCONPacket():
    PACKET_TYPES = {"SERVERDATA_AUTH" : 3,
                  "SERVERDATA_AUTH_RESPONSE" : 2,
                  "SERVERDATA_EXECCOMMAND" : 2,
                  "SERVERDATA_RESPONSE_VALUE" : 0}

    def __init__(self, id=0, type=0, body=""):
        """Creates a RCON packet."""
        self.id = id
        self.type = type
        self.body = ""
        self.terminator = b"\x00"

    def _check_int32(self, value):
        """
        :return: True if the value fits in a 32 bit signed int, False
        otherwise.
        :param value: a int
        """
        try:
            to_int32(value)
            return True
        except Exception:
            return False

    @property
    def type(self):
        """returns the packet type"""
        return self._type

    @type.setter
    def type(self, value):
        """Sets the packet type. raises a ValueError if the packet type is invalid"""
        if value not in RCONPacket.PACKET_TYPES.values():
            raise ValueError(f"{value!r} is not a valid value.")
        if self._check_int32(value):
            self._type = value
        else:
            raise ValueError(f"{value!r} is to large for a 32 bit signed int")

    @property
    def id(self):
        """:return: the id field of the packet."""
        return self._id

    @id.setter
    def id(self, value):
        """:param value: the new value for id. Has to fit into a 32 bit
        signed integer. Raises a ValueError if it does not fit."""
        if self._check_int32(value):
            self._id = value
        else:
            raise ValueError(f"{value!r} is to large for a 32 bit signed int")

    @property
    def body(self):
        """Returns the body of the packet."""
        return self._body

    @body.setter
    def body(self, value):
        """Sets the body to the given value and updates the packet size.
        The body is a regular python string. It is not encoded as bytearray!
        It also does not contain the Null-Termination."""
        if not isinstance(value, str):
            raise ValueError("body needs to be a string.")
        else:
            self._body = value

    @property
    def size(self):
        """Returns the size of the packet."""
        # 4 ID
        # 4 Type
        # X body
        # 1 terminator for body
        # 1 terminator of the packet
        return 4 + 4 + len(self._body) + 2*len(self.terminator)

    def msg(self):
        """Returns the complete message"""
        size = to_int32(self.size)
        id = to_int32(self.id)
        type = to_int32(self._type)

        return size + id + type + self._body.encode("ascii") + self.terminator + self.terminator

