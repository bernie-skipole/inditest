# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


"""Set to connect to two remote servers led1.py and led2.py
   Rather than using remote machines, these three services are all on
   one machine using different ports

   This adds logging, so a logfile is created, for the remote
   link to led1."""

## ignore these, used for development
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")

import logging
led1logger = logging.getLogger('indipydriver.remotelink')
led1fh = logging.FileHandler("logled1.log")
led1logger.addHandler(led1fh)
led1logger.setLevel(logging.DEBUG)


import asyncio
import indipydriver as ipd


if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625, debug_enable=True)
    server.add_remote(host="localhost", port=7626)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
