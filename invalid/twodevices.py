# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///


# This is to be compared with duplicatedevice2.py
# this has two separate device names and works
# whereas duplicatedevice2.py should fail

"One driver with two LED devices"

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

    """IPyDriver is subclassed here to create a driver
       controlling two LED devices."""

    async def rxevent(self, event):
        "On receiving data from the client, this is called"

        led1 = self.driverdata["led1"]
        led1name = f"LED_{led1.pin}"
        led2 = self.driverdata["led2"]
        led2name = f"LED_{led2.pin}"

        match event:

            case ipd.newSwitchVector(devicename=led1name,
                                     vectorname="ledvector") if 'ledmember' in event:
                # a new value has been received from the client
                ledvalue = event["ledmember"]
                # turn on or off the led
                if ledvalue == "On":
                    led1.on()
                elif ledvalue == "Off":
                    led1.off()
                else:
                    # not valid
                    return
                # and set this new value into the vector
                event.vector["ledmember"] = ledvalue
                # send the updated vector back to the client
                await event.vector.send_setVector()

            case ipd.newSwitchVector(devicename=led2name,
                                     vectorname="ledvector") if 'ledmember' in event:
                # a new value has been received from the client
                ledvalue = event["ledmember"]
                # turn on or off the led
                if ledvalue == "On":
                    led2.on()
                elif ledvalue == "Off":
                    led2.off()
                else:
                    # not valid
                    return
                # and set this new value into the vector
                event.vector["ledmember"] = ledvalue
                # send the updated vector back to the client
                await event.vector.send_setVector()



def make_device(led):
    "Creates a device"

    # create device name from the pin number
    ledname = "LED_" + str(led.pin)

    ledvalue = "On" if led.is_lit else "Off"

    # create switch member
    ledmember = ipd.SwitchMember(name="ledmember",
                                 label="LED Value",
                                 membervalue=ledvalue)
    # set this member into a vector
    ledvector = ipd.SwitchVector(name="ledvector",
                                 label=ledname,
                                 group="Control Group",
                                 perm="wo",
                                 rule='AtMostOne',
                                 state="Ok",
                                 switchmembers=[ledmember] )
    # return a Device with this vector
    return ipd.Device( devicename=ledname, properties=[ledvector])


def make_driver(led1, led2):
    "create a driver with two devices"

    leddevice1 = make_device(led1)
    leddevice2 = make_device(led2)

    # and return the driver
    return LEDDriver(leddevice1, leddevice2, led1=led1, led2=led2)


if __name__ == "__main__":

    # serve a driver containing two devices
    driver = make_driver(LED(17), LED(18))

    server = ipd.IPyServer(driver, host="localhost", port=7624, maxconnections=5)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
