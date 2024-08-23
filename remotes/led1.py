
"""Driver and server to control a (simulated) LED
   with devicename led1
   This is set to listen on port 7625 instead of 7624
   to test connections from serve_remotes.py enabling
   multiple connected servers to be run on a single machine"""


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


class LEDDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create an LED driver."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        # get the LED object controlling the instrument, which is
        # available in the named arguments dictionary 'self.driverdata'
        led = self.driverdata["led"]

        match event:

            # event.vector is the vector being requested or altered
            # event[membername] is the new value

            case ipd.getProperties():
                # An event of type 'getProperties' is a client request
                # to define a property. Send back a property definition
                await event.vector.send_defVector()

            case ipd.newSwitchVector(devicename="led1",
                                     vectorname="ledvector") if 'ledmember' in event:
                # a new value has been received from the client
                ledvalue = event["ledmember"]
                # turn on or off the led
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


def make_driver(led):
    "Creates the driver"

    # Note that “is_lit” is a property of the LED object
    # and is True if the LED is on, this is used to
    # set up the initial value of ledmember.

    ledvalue = "On" if led.is_lit else "Off"

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
    leddevice = ipd.Device( devicename="led1", properties=[ledvector])

    # Create the Driver containing this device, and the actual
    # LED object used for instrument control as a named argument
    driver = LEDDriver(leddevice, led=led)

    # and return the driver
    return driver


if __name__ == "__main__":

    # set up the LED pin and create and serve the driver
    led = LED(17)
    driver = make_driver(led)
    # set port at 7625 instead of 7624
    server = ipd.IPyServer(driver, host="localhost", port=7625, maxconnections=5)
    asyncio.run(server.asyncrun())
