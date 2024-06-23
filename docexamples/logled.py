
# Illustrates logging at level debug

# This saves logs, including xml traffic to file logfile.log


import logging
logger = logging.getLogger()

fh = logging.FileHandler("logfile.log")
logger.addHandler(fh)

logger.setLevel(logging.DEBUG)

import asyncio
import indipydriver as ipd

# Simulates an LED with a simple global variable

LED = 'Off'

class LEDDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"
        global LED

        match event:

            # event.vector is the vector being requested or altered
            # event[membername] is the new value

            case ipd.getProperties():
                # An event of type 'getProperties' is a client request
                # to define a property. Send back a property definition
                await event.vector.send_defVector()

            case ipd.newSwitchVector(devicename="led",
                                     vectorname="ledvector") if 'ledmember' in event:
                # a new value has been received from the client
                LED = event["ledmember"]
                # and set this new value into the vector
                event.vector["ledmember"] = LED
                # send the updated vector back to the client
                await event.vector.send_setVector()

def make_driver():
    "Creates the driver"

    # create switch member
    ledmember = ipd.SwitchMember(name="ledmember",
                                 label="LED Value",
                                 membervalue=LED)
    # set this member into a vector
    ledvector = ipd.SwitchVector(name="ledvector",
                                 label="LED",
                                 group="Control Group",
                                 perm="rw",
                                 rule='AtMostOne',
                                 state="Ok",
                                 switchmembers=[ledmember] )
    # create a Device with this vector
    led = ipd.Device( devicename="led", properties=[ledvector])

    # Create the Driver containing this device
    driver = LEDDriver([led])

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer([driver], host="localhost", port=7624, maxconnections=5)
    asyncio.run(server.asyncrun())
