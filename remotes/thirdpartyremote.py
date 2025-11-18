# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipyserver"
# ]
# ///

"""Connect to third party 'indiserver' process.

Run indiserver in one process:

indiserver indi_simulator_telescope

and this script in another process - which makes a remote connection to indiserver.

indipyterm can then connect to either
7624 - in which it will connect to indiserver, or
7625 - in which it will connect to this indipyserver

In both cases the terminal should pick up, and be able to control indi_simulator_telescope

"""


import asyncio
from indipyserver import IPyServer, version


if __name__ == "__main__":


    # run this server on port 7625 to avoid clashing with indiserver on 7624
    server = IPyServer(host="localhost", port=7625, maxconnections=5)
    server.add_remote(host="localhost", port=7624)
    print(f"Running {__file__} with indipyserver version {version}")
    asyncio.run(server.asyncrun())
