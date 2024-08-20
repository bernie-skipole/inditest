
# for my own testing, please ignore
import sys
sys.path.insert(0, "/home/bernie/git/indipydriver")
sys.path.insert(0, "/home/bernie/git/indipyclient")


import asyncio
import indipydriver as ipd



if __name__ == "__main__":

    server = ipd.IPyServer(host="localhost", port=7624, maxconnections=5)

    # connect to two remote servers
    server.add_remote(host="localhost", port=7625)
    server.add_remote(host="localhost", port=7626)
    asyncio.run(server.asyncrun())
