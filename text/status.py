# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.1.0",
#     "indipyserver"
# ]
# ///


import asyncio
import logging, sys, random

import indipydriver as ipd

from indipyserver import IPyServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)



class RODriver(ipd.IPyDriver):
    """IPyDriver is subclassed here"""

    async def hardware(self):
        """Sends an Idle after switch is turned off"""

        rovector1 = self['rodevice']['rovector1']
        rovector2 = self['rodevice']['rovector2']
        while not self.stop:
            await asyncio.sleep(1)
            rint = random.randint(0,1)
            if rint:
                await rovector1.send_setVector(state="Alert", allvalues=False)
                await rovector2.send_setVector(state="Idle", allvalues=False)
            else:
                await rovector1.send_setVector(state="Idle", allvalues=False)
                await rovector2.send_setVector(state="Alert", allvalues=False)


def make_driver():
    "Returns an instance of the driver"

    # create a member and vector for status one
    romember1 = ipd.TextMember( name="romember1",
                                label = "Status",
                                membervalue="Zero")
    rovector1 = ipd.TextVector( name = 'rovector1',
                                label = "Zero",
                                group = 'Status',
                                perm = "ro",
                                state = "Ok",
                                textmembers = [romember1])

    romember2 = ipd.TextMember( name="romember2",
                                label = "Status",
                                membervalue="One")
    rovector2 = ipd.TextVector( name = 'rovector2',
                                label = "One",
                                group = 'Status',
                                perm = "ro",
                                state = "Ok",
                                textmembers = [romember2])


    # create a device with the two vectors
    rodevice = ipd.Device( devicename="rodevice",
                           properties=[rovector1, rovector2] )

    # Create the Driver, containing this Device
    driver = RODriver( rodevice )

    # and return the driver
    return driver


if __name__ == "__main__":
    # serve the driver on localhost, port 7624
    driver = make_driver()
    # enable debugging
    driver.debug_enable = True
    server = IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
