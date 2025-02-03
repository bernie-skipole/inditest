# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


"""This illustrates IPyServer working with executable drivers
   and requires these simulator drivers to be installed
   using something like "apt install indi-bin"""


import asyncio

from indipydriver import IPyServer

server = IPyServer(host="localhost",
                   port=7624,
                   maxconnections=5)

server.add_exdriver("indi_simulator_telescope")
server.add_exdriver("indi_simulator_ccd")
print(f"Running {__file__}")
asyncio.run(server.asyncrun())
