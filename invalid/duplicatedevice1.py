# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "indipydriver",
# ]
# ///


"Two drivers, both with the same devicename"

# Duplicate device names should
# cause a failure

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

        led = self.driverdata["led"]

        match event:

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newSwitchVector(devicename="led",
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
    leddevice = ipd.Device( devicename="led", properties=[ledvector])

    # and return the driver
    return LEDDriver(leddevice, led=led)


if __name__ == "__main__":

    # serve two drivers with duplicate device names
    driver1 = make_driver(LED(17))
    driver2 = make_driver(LED(18))
    server = ipd.IPyServer(driver1, driver2, host="localhost", port=7624, maxconnections=5)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
