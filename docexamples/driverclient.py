
import asyncio

from indipyclient.console import ConsoleClient
from example1 import make_driver, ThermalControl


async def monitor(client, driver, thermalcontrol):
    """This monitors the client, if it shuts down,
       then shut down the driver and the instrument"""
    await client.stopped.wait()
    # the client has stopped
    driver.shutdown()
    thermalcontrol.shutdown()


async def main(client, driver, thermalcontrol):
    """Run the client, driver and instrument together,
       also with monitor to check if client quit is chosen"""
    try:
        await asyncio.gather(client.asyncrun(),
                             driver.asyncrun(),
                             thermalcontrol.run_thermostat(),
                             monitor(client, driver, thermalcontrol))
    except asyncio.CancelledError:
        # avoid outputting stuff on the command line
        pass
    finally:
        # clear curses setup
        client.console_reset()


if __name__ == "__main__":

    # Make an instance of the object controlling the instrument
    thermalcontrol = ThermalControl()
    # make a driver for the instrument
    thermodriver = make_driver(thermalcontrol)

    # set driver listening on localhost
    thermodriver.listen()
    # create a ConsoleClient calling localhost
    client = ConsoleClient()
    # run all coroutines
    asyncio.run( main(client, thermodriver, thermalcontrol) )
