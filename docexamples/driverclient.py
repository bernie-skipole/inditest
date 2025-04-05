# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
#     "indipyclient"
# ]
# ///

"""
Runs the console terminal client and the Thermostat driver together
"""

import asyncio

# stop anything going to the screen
import logging
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

from indipyclient.console import ConsoleClient
from indipydriver import IPyServer
from example1 import make_driver

async def main(client, server):
    """Run the client and server"""

    # start the server
    servertask = asyncio.create_task( server.asyncrun() )

    # start the client, and wait for it to close
    try:
        await client.asyncrun()
    finally:
        # Ensure the terminal is cleared
        client.console_reset()
    print("Shutting down, please wait")

    # ask the server to stop
    server.shutdown()

    # wait for the server to shutdown
    await servertask



if __name__ == "__main__":

    # make a driver for the thermostat
    thermodriver = make_driver("Thermostat", 15)
    # create server listening on localhost
    server = IPyServer(thermodriver)
    # create a ConsoleClient calling localhost
    client = ConsoleClient()
    # run all coroutines
    asyncio.run( main(client, server) )
