
# Driver to control a bank of (simulated) LEDs so this
# can be run on a PC without gpiozero

import asyncio
import indipydriver as ipd


class LED:
    "A class to simulate gpiozero.LED"

    def __init__(self, pin):
        self.pin = pin
        self.is_lit = False

    def on(self):
        self.is_lit = True

    def off(self):
        self.is_lit = False


class _LEDDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create a driver
       which controls all the given LEDs."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        if isinstance(event, ipd.newSwitchVector) and event.devicename in self.driverdata:

            # get the LED object associated with this devicename
            ledobject = self.driverdata[event.devicename]

            # event.vector is the vector being requested or altered
            # event[membername] is the new value.

            if event.vectorname == "ledvector" and 'ledmember' in event:
                # a new value has been received from the client
                ledvalue = event["ledmember"]
                # turn on or off the led
                if ledvalue == "On":
                    ledobject.on()
                elif ledvalue == "Off":
                    ledobject.off()
                else:
                    # not valid
                    return
                # and set this new value into the vector
                event.vector["ledmember"] = ledvalue
                # send the updated vector back to the client
                await event.vector.send_setVector()


def make_driver(*pins):
    "Creates the driver"

    # Note that “is_lit” is a property of the LED object
    # and is True if the LED is on, this is used to
    # set up the initial value of ledmember.

    objdict = {}
    devicelist = []

    for pin in pins:
        devicename = f"LED_{pin}"
        ledobject = LED(pin)

        # add this object to objdict, with key devicename
        objdict[devicename] = ledobject

        ledvalue = "On" if ledobject.is_lit else "Off"

        # create switch member
        ledmember = ipd.SwitchMember(name="ledmember",
                                     label="LED Value",
                                     membervalue=ledvalue)
        # set this member into a vector
        ledvector = ipd.SwitchVector(name="ledvector",
                                     label="LED",
                                     group="Control Group",
                                     perm="wo",
                                     rule='AtMostOne',
                                     state="Ok",
                                     switchmembers=[ledmember] )
        # create a Device with this vector and add it to the list
        devicelist.append( ipd.Device( devicename, properties=[ledvector]) )


    # Create the Driver containing these devices, and as named argument
    # add the devicename:LED object dictionary.
    # This is a convenient way of linking device to controlling object
    driver = _LEDDriver(*devicelist, **objdict )

    # and return the driver
    return driver


if __name__ == "__main__":

    # create and serve the driver
    # in this case a driver operating pins 16,17 and 18
    driver = make_driver(16,17,18)
    server = ipd.IPyServer(driver, host="localhost", port=7624, maxconnections=5)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
