
"""Set to connect to two remote servers led1.py and led2.py
   Rather than using remote machines, these three services are all on
   one machine using different ports"""

## ignore these, used for development
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")


import asyncio
import indipydriver as ipd


if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
