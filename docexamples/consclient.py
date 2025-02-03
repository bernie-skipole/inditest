# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///


"""Script dedicated to a terminal connecting
   to a set host and port"""

import asyncio

# stop anything going to the screen
import logging
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

from indipyclient.console import ConsoleClient

# create a ConsoleClient calling host and port
client = ConsoleClient(indihost="raspberrypi", indiport=7624)

try:
    # Starts the client, creates the console screens
    asyncio.run(client.asyncrun())
finally:
    # clear curses setup
    client.console_reset()
