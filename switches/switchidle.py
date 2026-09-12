# /// script
# requires-python = ">=3.11"
# ///


"""A single switch, with idle sent after switch is turned off

Logger level is set to debug, and prints debug logs"""


import asyncio
import logging, sys

import indipydriver as ipd
from indipyserver import IPyServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class SWDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create a driver."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        if event.devicename != "Switch":
            # No other device data is expected, ignore anything
            # without the correct devicename
            return

        # event.vector is the vector being requested or altered
        # event['swmember'] is the new value.

        if isinstance(event, ipd.newSwitchVector):
            if event.vectorname == "swvector" and 'swmember' in event:
                # a new value has been received from the client
                # set this new value into the vector and
                # send the updated vector back to the client
                if event['swmember'] == "On":
                    event.vector["swmember"] = "On"
                    await event.vector.send_setVector(state="Ok", message="Turned On")
                else:
                    event.vector["swmember"] = "Off"
                    await event.vector.send_setVector(state="Ok", message="Turned Off")
                    # Note the state could be set to Idle here, but I want to illustrate allvalues=False

    async def hardware(self):
        """Sends an Idle after switch is turned off"""

        swvector = self['Switch']['swvector']
        while not self.stop:
            await asyncio.sleep(1)
            if swvector['swmember'] == "Off":
                await swvector.send_setVector(state="Idle", message="System Off, now Idle", allvalues=False)

        # When the switch is turned Off, this idle will be sent, but since allvalues is False
        # it will only be transmitted once.
        # Each time it is not sent a debug message will be created which can be viewed if
        # debug logging is enabled.


def make_driver():
    "Creates the driver"

    # create switch member, note: starting with switch Off.
    swmember = ipd.SwitchMember(name="swmember",
                                 label="Big Switch",
                                 membervalue="Off")
    # set this member into a vector
    swvector = ipd.SwitchVector(name="swvector",
                                 label="Big Switch",
                                 group="Control Group",
                                 perm="wo",
                                 rule='AtMostOne',
                                 state="Ok",
                                 switchmembers=[swmember] )
    # create a Device with this vector
    device = ipd.Device( "Switch", properties=[swvector])

    # Create the Driver containing this device
    driver = SWDriver(device)

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
