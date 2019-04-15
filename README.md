# rcon-server
A implementation of the RCON protocol on the server side.

# Why do you need an RCON server implementation?

rcon-server is primarily designed as a tool for testing, e.g. with unit tests.
Installing, running, updating, etc a regular srcds server might use a lot of
resources.
\>10GB of storage space per server is not uncommon.
Also it is hard to get some results from an server in a test environment.
A server only reports the amount of users which are on the server.
Getting several people on a server for testing is pretty annoying and time
consuming.
rcon-server allows you to implement a function that returns an answer per
command.

# Specification

The RCON Specification can be found here:
[https://developer.valvesoftware.com/wiki/Source_RCON_Protocol]

# how to run the tests:

~~~
cd rcon_server
python3 -m unittest
~~~
