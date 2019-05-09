from rcon_packet import RCONPacket

class RCONMessage:
    """
    A RCONMessage represents a message which may consist of multiple packets.
    """

    def __init__(self, packet=[]):
        """
        creates a new RCONMesage object.

        :param packet: a RCONPacket or a list of RCONPackets. May be empty.
        """
        if isinstance(packet, RCONPacket):
            packet = [packet]
        assert isinstance(packet, list)
        self.packets = packet

    def add_packet(self, packet):
        """
        Add an RCONPacket to the message.

        :param packet: a RCONPacket.
        """
        assert isinstance(packet, RCONPacket)
        self.packets.append(packet)

    def __iter__(self):
        """Returns an iterator over the packets."""
        return iter(self.packets)

    def msg(self):
        """Return the whole message as a bytearray."""
        return b"".join(p.msg() for p in self.packets)

    @property
    def body(self):
        """
        Returns the body of the message. This is the body of all packets joined
        together.
        """
        return "".join(p.body for p in self.packets)
