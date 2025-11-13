# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.0.2",
#     "indipyserver"
# ]
# ///

#ignore these lines, used during testing
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")

"""Connects to two remote servers led1.py and led2.py
   Rather than using remote machines, these three services are all on
   one machine using different ports. The duplicate names on the remote connections should
   be detected and cause the server to shutdown"""

import asyncio
import indipydriver as ipd

from indipyserver import IPyServer


if __name__ == "__main__":

    server = IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    print(f"Running {__file__} with indipydriver version {ipd.version}")
    asyncio.run(server.asyncrun())
