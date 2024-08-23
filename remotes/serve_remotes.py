
"""Set to connect to two remote servers led1.py and led2.py
   Rather than using remote machines, these three services are all on
   one machine using different ports"""

import asyncio
import indipydriver as ipd


if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    asyncio.run(server.asyncrun())
