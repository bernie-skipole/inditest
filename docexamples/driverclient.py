
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")
#sys.path.insert(0, "/home/bernard/git/indipyclient")

import asyncio

from indipyclient.console import ConsoleClient
from example1 import make_driver


async def monitor(client, driver):
    "This monitors the client, if it shuts down, it shuts down the driver"
    while not client.stop:
        await asyncio.sleep(0.2)
    # the client has stopped, shut down the driver
    driver.shutdown()


async def main(client, driver):
    "Run the driver and client together"
    try:
        await asyncio.gather(client.asyncrun(), driver.asyncrun(), monitor(client, driver))
    except asyncio.CancelledError:
        # avoid outputting stuff on the command line
        pass
    finally:
        # clear curses setup
        client.console_reset()


if __name__ == "__main__":

    # Get driver, in this case from example1
    driver = make_driver()
    # set driver listening on localhost
    driver.listen()
    # create a ConsoleClient listening on localhost
    client = ConsoleClient()
    # run them
    asyncio.run(main(client, driver))
