# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipyserver"
# ]
# ///


"""Set to connect to two remote servers led1.py and led2.py
   Rather than using remote machines, these are on
   one machine using different ports

   This adds logging, so a logfile is created, for the remote
   link to led1."""

import logging
led1logger = logging.getLogger('indipyserver.remote')
led1fh = logging.FileHandler("logled1.log")
led1logger.addHandler(led1fh)
led1logger.setLevel(logging.DEBUG)


import asyncio
from indipyserver import IPyServer, version


if __name__ == "__main__":

    server = IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625, debug_enable=True)
    server.add_remote(host="localhost", port=7626)
    print(f"Running {__file__} with indipyserver version {version}")
    asyncio.run(server.asyncrun())
