from util import to_int32, from_int32, check_int32

class RCONPacket():

    # The number 2 is there in two cases.
    # this is intended by the protocol.
    # AUTH_RESPONSE is only send server -> client
    # and EXECCOMMAND is only send client -> server
    # Therefore there should be no case in which
    # a packet could be missunderstood due to the identical packet type
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0

    PACKET_TYPES = [SERVERDATA_AUTH, SERVERDATA_AUTH_RESPONSE,
                    SERVERDATA_EXECCOMMAND, SERVERDATA_RESPONSE_VALUE]

    def __init__(self, id=0, type=0, body=""):
        """Creates a RCON packet."""
        self.id = id
        self.type = type
        self.body = body
        self.terminator = b"\x00"

    @classmethod
    def from_buffer(cls, buffer):
        """Tries to build a RCONPacket from the given buffer.
        This method only builds one packet.
        :return: a tuple with an RCONPacket and the remaining buffer if a
        whole packet was received. A tuple with None and the remaining buffer
        otherwise.
        :param buffer: The buffer as a bytestring.
        """
        if len(buffer) > 12:
            size = from_int32(buffer[0:4])  # TODO check for malformed packages
                                            # size can not be < 10
                                            # maybe raise Exception
            assert size >= 10, "Packet size can not be smaller than 10"
            id = from_int32(buffer[4:8])
            type = from_int32(buffer[8:12])

            # check if the buffer is long enough to fit the body
            # first 4 bytes are for the size
            if len(buffer) >= 4 + size:
                # +4 for the size, -2 for the 2 \x00 at the end
                body = buffer[12:size+4-2].decode("ascii")
                remaining_buffer = buffer[size+4:]
                packet = cls(id, type, body)
                return (packet, remaining_buffer)

        return (None, buffer)


    @property
    def type(self):
        """returns the packet type"""
        return self._type

    @type.setter
    def type(self, value):
        """Sets the packet type. raises a ValueError if the packet type is invalid"""
        if value not in RCONPacket.PACKET_TYPES:
            raise ValueError(f"{value!r} is not a valid value.")
        if check_int32(value):
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
        if check_int32(value):
            self._id = value
        else:
            raise ValueError(f"{value!r} is to large for a 32 bit signed int")

    @property
    def body(self):
        """Returns the body of the packet."""
        return self._body

    @body.setter
    def body(self, value):
        """Sets the body to the given value.
        The body is a regular python string. It is not encoded as bytearray!
        It also does not contain the null termination."""
        if not isinstance(value, str):
            raise ValueError("body needs to be a string.")
        else:
            self._body = value

    @property
    def size(self):
        """Return the size of the packet."""
        # 4 ID
        # 4 Type
        # X body
        # 1 terminator for body
        # 1 terminator of the packet
        return 4 + 4 + len(self._body) + 2*len(self.terminator)

    def msg(self):
        """
        Returns a bytearray which may consist of multiple RCONPackets
        directly after each other if the body is to large for one packet.
        """
        size = to_int32(self.size)
        id = to_int32(self.id)
        type = to_int32(self._type)

        return size + id + type + self._body.encode("ascii") + self.terminator + self.terminator

    def __repr__(self):
        return f"<RCONPacket type={self.type}, id={self.id}, body={self.body}>"
