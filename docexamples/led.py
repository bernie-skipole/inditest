
# Driver to control an LED on a Raspberry Pi

import asyncio
import indipydriver as ipd

from gpiozero import LED

led = LED(17)

class LEDDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

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
                ledvalue = event["ledmember"]
                if ledvalue == "On":
                    led.on()
                elif ledvalue == "Off":
                    led.off()
                else:
                    # not valid
                    return
                # and set this new value into the vector
                event.vector["ledmember"] = ledvalue
                # send the updated vector back to the client
                await event.vector.send_setVector()


def make_driver():
    "Creates the driver"

    ledvalue = "On" if led.is_lit else "Off"

    # create switch member
    ledmember = ipd.SwitchMember(name="ledmember",
                                 label="LED Value",
                                 membervalue=ledvalue)
    # set this member into a vector
    ledvector = ipd.SwitchVector(name="ledvector",
                                 label="LED",
                                 group="Control Group",
                                 perm="rw",
                                 rule='AtMostOne',
                                 state="Ok",
                                 switchmembers=[ledmember] )
    # create a Device with this vector
    leddevice = ipd.Device( devicename="led", properties=[ledvector])

    # Create the Driver containing this device
    driver = LEDDriver([leddevice])

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer([driver], host="localhost", port=7624, maxconnections=5)
    asyncio.run(server.asyncrun())
