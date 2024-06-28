# This illustrates IPyServer working with executable drivers
# and requires these simulator drivers to be installed
# using something like "apt install indi-bin"


import asyncio

# uncomment to enable logging
#
# import logging
# logger = logging.getLogger()
# fh = logging.FileHandler("logfile.log")
# logger.addHandler(fh)
# logger.setLevel(logging.DEBUG)

from indipydriver import IPyServer

server = IPyServer([], host="localhost",
                       port=7624,
                       maxconnections=5)

server.add_exdriver("indi_simulator_telescope")
server.add_exdriver("indi_simulator_ccd")
asyncio.run(server.asyncrun())
