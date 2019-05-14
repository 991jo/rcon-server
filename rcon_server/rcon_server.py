import asyncio
import logging

from .rcon_connection import RCONConnection

logger = logging.getLogger(name="RCONServer")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

class RCONServer:
    def __init__(self, bind=("localhost",27015), password=None):
        """Initializes a RCON Server.
        :param bind: a tuple (address, port) to bind to
        :password: the RCON password
        """
        self.connections = [] # list of all connections
                              # the connections append and remove themselves
                              # to/from it
        self.set_password(password)
        self.bind = bind

    @property
    def password(self):
        """:return: The RCON password as str"""
        return self._password

    def connection_factory(self):
        conn = RCONConnection(self)
        return conn

    def check_password(self, pw):
        """
        :return: True if the given password *pw* matches the RCON password.
        False otherwise or if the RCON password is the empty string or None.
        """
        if self.password == "" or self.password is None:
            return False
        return self.password == pw

    def set_password(self, password):
        """Used to set the RCON password.
        If this function is called all authenticated connections are closed.
        :param password: the new rcon password.
        """
        if password is None or isinstance(password,str):
            self._password = password
        else:
            raise ValueError("password needs to be a string or None.")
        for conn in self.connections:
            if conn.state != "unauthenticated":
                conn.close_connection()

    async def listen(self):
        """Starts listening on the socket and handling requests."""

        self._loop = asyncio.get_event_loop()
        server = await self._loop.create_server(self.connection_factory,
                                          self.bind[0], self.bind[1])
        print(server)
        async with server:
            logger.info("starting server")
            for socket in server.sockets:
                logger.info("listening on %s:%s" % socket.getsockname())
            await server.serve_forever()

    def handle_execcommand(self, packet, connection):
        """
        Handles an EXECCOMMAND package. This command has to be implemented by
        a subclass of the RCONServer.
        :param packet: the packet containing the command
        :param connection: the RCONConnection which calls this method
        """
        raise NotImplementedError("This method is not implemented! A subclass "
                                  "must implement this method!")

if __name__ == "__main__":
    server = RCONServer()
    asyncio.run(server.listen())
