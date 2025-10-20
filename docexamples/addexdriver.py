# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipyserver",
# ]
# ///


"""This illustrates IPyServer working with executable drivers
   and requires these simulator drivers to be installed
   using something like "apt install indi-bin"""



import asyncio

import logging, sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


from indipyserver import IPyServer

server = IPyServer(host="localhost",
                   port=7624,
                   maxconnections=5)

server.add_exdriver("indi_simulator_telescope")
server.add_exdriver("indi_simulator_ccd")
print(f"Running {__file__}")
asyncio.run(server.asyncrun())
