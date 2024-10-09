
"""
Runs the console terminal client and the Thermostat driver together
"""

import asyncio

# stop anything going to the screen
import logging
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

from indipyclient.console import ConsoleClient
from example1 import make_driver

async def main(client, driver):
    """Run the client and driver"""

    # start the driver
    drivertask = asyncio.create_task( driver.asyncrun() )

    # start the client, and wait for it to close
    try:
        await client.asyncrun()
    finally:
        # Ensure the terminal is cleared
        client.console_reset()
    print("Shutting down, please wait")

    # ask the driver to stop
    driver.shutdown()

    # wait for the driver to shutdown
    await drivertask



if __name__ == "__main__":

    # make a driver for the thermostat
    thermodriver = make_driver("Thermostat", 15)
    # set driver listening on localhost
    thermodriver.listen()
    # create a ConsoleClient calling localhost
    client = ConsoleClient()
    # run all coroutines
    asyncio.run( main(client, thermodriver) )
