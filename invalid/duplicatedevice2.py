
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


def make_device(led):
    "Creates a device"

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
    # return a Device with this vector
    return ipd.Device( devicename="led", properties=[ledvector])


def make_driver(led):

    # create a driver with two device names
    leddevice1 = make_device(led)
    leddevice2 = make_device(led)

    # and return the driver
    return LEDDriver(leddevice1, leddevice2, led=led)


if __name__ == "__main__":

    # serve a driver containing two devices with duplicate device names
    driver = make_driver(LED(17))

    server = ipd.IPyServer(driver, host="localhost", port=7624, maxconnections=5)
    asyncio.run(server.asyncrun())
