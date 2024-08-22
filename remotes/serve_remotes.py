
# for my own testing, please ignore
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")
#sys.path.insert(0, "/home/bernard/git/indipyclient")

#import logging
#logger = logging.getLogger()
#fh = logging.FileHandler("logfile.log")
#logger.addHandler(fh)
#logger.setLevel(logging.DEBUG)

import asyncio
import indipydriver as ipd


if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    asyncio.run(server.asyncrun())
