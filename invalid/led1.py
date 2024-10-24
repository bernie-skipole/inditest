
"""Driver and server to control a (simulated) LED
   This is set to listen on port 7625 instead of 7624
   to test connections from serve_remotes.py enabling
   multiple connected servers to be run on a single machine

   In this case the devicename is set to led to be duplicate
   with the device in led2.py, this being a test to ensure
   the server detects a duplicate devicename"""



# Driver to control a (simulated) LED so this can be run
# on a PC without gpiozero

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

    """IPyDriver is subclassed here to create an LED driver."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        # get the LED object controlling the instrument, which is
        # available in the named arguments dictionary 'self.driverdata'

        ledobject = self.driverdata["ledobj"]

        # event.vector is the vector being requested or altered
        # event[membername] is the new value.

        # There is only one device in this driver,
        # so no need to check devicename

        if isinstance(event, ipd.newSwitchVector):
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


def make_driver(devicename, pin):
    "Creates the driver"

    # Note that “is_lit” is a property of the LED object
    # and is True if the LED is on, this is used to
    # set up the initial value of ledmember.

    ledobject = LED(pin)
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
    # create a Device with this vector
    leddevice = ipd.Device( devicename, properties=[ledvector])

    # Create the Driver containing this device, and as named argument
    # add the LED object used for instrument control
    driver = _LEDDriver(leddevice, ledobj=ledobject )

    # and return the driver
    return driver


if __name__ == "__main__":

    # create and serve the driver
    # the devicename has to be unique in a network of devices,

    # in this case the devicename is "led", pin 17
    driver = make_driver("led", 17)
    server = ipd.IPyServer(driver, host="localhost", port=7625, maxconnections=5)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
